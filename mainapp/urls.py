from django.urls import path, include
from mainapp.views import RegisterView, VerifyEmail

urlpatterns = [
    path('registration/', RegisterView.as_view({"post": "registration"}), name='register'),
    path("email-verify/", VerifyEmail.as_view(), name='email-verify'),
]