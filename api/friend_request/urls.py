from django.urls import path
from .views import FriendRequest, ListUsers, SearchAPIView, SendRequestView

urlpatterns = [
    path('send/', SendRequestView.as_view()),
    path('accept/', FriendRequest.as_view({'put':'update'})),
    path('reject/', FriendRequest.as_view({'delete':'destroy'})),
    path('list/<str:pending_status>/', ListUsers.as_view()), 
    path('search/', SearchAPIView.as_view())
]
