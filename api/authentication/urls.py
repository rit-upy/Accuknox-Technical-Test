from django.urls import path
from .views import SignupAPIView, LoginAPIView
urlpatterns = [
    path('login/', LoginAPIView.as_view() ),
    path('signup/', SignupAPIView.as_view())
]
