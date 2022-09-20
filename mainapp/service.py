from rest_framework.response import Response
from rest_framework import status

from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings

import jwt


def email_link(request, token):
    current_site = get_current_site(request).domain
    relativeLink = reverse('email-verify')
    url = 'http://'+current_site+relativeLink+"?token="+str(token)
    return url


def create_token(**kwargs):
    
    data = {
        **kwargs
    }
    try:
        token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")
        return token
    except jwt.ExpiredSignatureError:
        return Response({'error': 'DecodeError'}, status=status.HTTP_400_BAD_REQUEST)