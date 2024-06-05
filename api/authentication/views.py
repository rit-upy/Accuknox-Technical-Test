from rest_framework import views,generics,status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, SignUpSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .models import User
# Create your views here.
class SignupAPIView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class LoginAPIView(views.APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self,request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['user_email']
        password = serializer.validated_data['password']
        
        
        try:
            user = User.objects.get(email__iexact = email)
        except User.DoesNotExist:
            return Response('User email not found', status = status.HTTP_401_UNAUTHORIZED)
        
        
        if not user.check_password(password):
            return Response('Wrong password!!', status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


