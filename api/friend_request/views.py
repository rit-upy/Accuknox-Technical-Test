
from rest_framework import generics,status
from .models import Friends
from authentication.models import User
from .serializers import AcceptedUsersSerializer,SearchUsersSerializer,RequestSerializer, SendRequestSerializer, ReceivedUserRequestSerializer
from rest_framework.response import Response
from rest_framework import viewsets
from django.db.models import Q
from rest_framework import throttling
from rest_framework.pagination import PageNumberPagination



# Create your views here.
class ListUsers(generics.ListAPIView):
    
    serializer_class = AcceptedUsersSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        pending_status = kwargs.get('pending_status')        

        if not pending_status:
            return Response('Status not provided', status=status.HTTP_400_BAD_REQUEST)
        elif pending_status.lower() == 'accepted':
            friends = Friends.objects.filter(user = user, pending = False)            
        elif pending_status.lower() == 'pending':
            self.serializer_class = ReceivedUserRequestSerializer
            friends = Friends.objects.filter(friend = user, pending = True) 
        else:
            return Response('Wrong status request!', status=status.HTTP_400_BAD_REQUEST)
        
        
        if len(friends) == 0:
            return Response(f'You have no {pending_status} friend requests', status=status.HTTP_200_OK)
        self.queryset = friends
        
        return super().get(request, *args, **kwargs)


class SearchUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000
       

class SearchAPIView(generics.ListAPIView):
    serializer_class = SearchUsersSerializer
    pagination_class = SearchUserPagination
    
    def get_queryset(self):
        search_email = self.request.query_params.get('email', None)

        if search_email is not None:
            return User.objects.filter(email=search_email)
        
        name = self.request.query_params.get('name', None)
        
        if name is not None:
            
            return User.objects.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
        return Response('Please enter the email or the name field.',\
                             status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # if not queryset.exists():
        #     return Response('Please enter the email or the name field.', status=status.HTTP_400_BAD_REQUEST)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class FriendRequestThrottle(throttling.SimpleRateThrottle):
    scope = 'friend_request'
    rate = '3/minute'
    def get_cache_key(self, request, view):
        # Use the user's ID as part of the cache key to distinguish requests from different users
        user_id = request.user.id if request.user else None
        return f'{self.scope}-{user_id}'

    def allow_request(self, request, view):
        # Get the cache key for the current request
        cache_key = self.get_cache_key(request, view)
        # Get the number of requests made by the user within the throttle time window
        num_requests = self.cache.get(cache_key, 0)
        # Check if the user has exceeded the allowed number of requests
        if num_requests >= 3:
            return False
        # Increment the number of requests made by the user
        self.cache.set(cache_key, num_requests + 1, self.duration)
        return True


class FriendRequest(viewsets.ModelViewSet):
    
    serializer_class = RequestSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        friend = request.data['friend']

        if Friends.objects.filter(user = user, friend = friend).exists():
            return Response('You cannot accept your own friend request. You must wait for the other person.'
                            , status=status.HTTP_400_BAD_REQUEST)
        try:
            friend = Friends.objects.get(user = friend, friend = user, pending = True) #accepting request
        except Friends.DoesNotExist:
            return Response('The request seems to be wrong. Check again', status=status.HTTP_400_BAD_REQUEST)
        friend.pending = False
        friend.save()
        return Response('Friend request is accepted.', status=status.HTTP_200_OK)
    
    def get_throttles(self):
        if self.action == 'create':
            return [FriendRequestThrottle()]
        return super().get_throttles()

    def destroy(self, request, *args, **kwargs): #reject
        user = request.user
        friend_id = request.data['friend']
        if user.id == friend_id:
            return Response('User and friend are the same', status=status.HTTP_400_BAD_REQUEST)
        

        try:
            friend = Friends.objects.get(user__id = friend_id , friend = user )
        except Friends.DoesNotExist:
            return Response('Friend request does not exist.', status=status.HTTP_400_BAD_REQUEST)
        
        if friend.pending is False:
            return Response('Request is already accepted and can\'t be deleted', status=status.HTTP_400_BAD_REQUEST)
        
        friend.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SendRequestView(generics.CreateAPIView):
    serializer_class = SendRequestSerializer
    