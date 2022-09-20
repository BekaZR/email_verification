from mainapp.serializers import RegisterSerializer
from rest_framework.response import Response
from mainapp.models import User
import jwt
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from mainapp.service import create_token, email_link
from mainapp.tasks import send_mail_to_email
from rest_framework import status, viewsets
from django.conf import settings


class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    @action(methods=['post'], detail=False, serializer_class=RegisterSerializer, permission_classes = [AllowAny])
    def registration(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        token = create_token(user_id=serializer.data.get("id"))
        
        url = email_link(request, token)
        
        send_mail_to_email.delay(serializer.data.get("email"), url)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmail(ListAPIView):
    def get(self, request):
        
        token = request.query_params.get('token', None)
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
