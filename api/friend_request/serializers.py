from rest_framework import serializers, status
from .models import Friends, User

from rest_framework.response import Response

class AcceptedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = ('friend', )

class ReceivedUserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = ('user',)

class SearchUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'full_name')


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = ['friend', ]

    def update(self, instance, validated_data): #accept friend request
        print('The serializer for accepting the friend request is being called')

        user = self.context['request'].user
        friend = validated_data['friend']

        #check for whether user exists in table
        user_friend_exists = Friends.objects.filter(user = user, friend = friend, pending = True)
        reverse_user_friend_exists = Friends.objects.filter(user = friend, friend = user, pending = True)
        if not user_friend_exists.union(reverse_user_friend_exists).exists():
            return Response('You must send a friend request before it can be accepted', status = status.HTTP_400_BAD_REQUEST)
        
        #check for duplicate friend request
        user_friend_check_accept = Friends.objects.filter(user = user , friend = friend, pending = False)
        reverse_user_friend_check_accept = Friends.objects.filter(user = friend, friend = user, pending = False)
        if user_friend_check_accept.union(reverse_user_friend_check_accept).exists():
            return Response('Duplicate accept friend request', status=status.HTTP_400_BAD_REQUEST)
        
        validated_data['pending'] = False
        validated_data['user'] = user
        return super().update(instance, validated_data)


class SendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = ('friend', )    

    def create(self, validated_data): #creating only one record for the friendship table
        user = self.context['request'].user
        friend = validated_data['friend']
       # Check for duplicate friend request
       
        if Friends.objects.filter(user=user, friend=friend, pending=True).exists():
            raise serializers.ValidationError('Friend request already sent to this user')
        if Friends.objects.filter(user=friend, friend=user, pending=True).exists(): # Check if a reverse request already exists
            raise serializers.ValidationError('Friend request already received from this user')


        # Create the friend request
        validated_data['pending'] = True
        validated_data['user'] = user
        return super().create(validated_data) 