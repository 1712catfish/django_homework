from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework.authtoken.models import Token


def token_login(request, user):
    token, _ = Token.objects.get_or_create(user=user)
    if settings.CREATE_SESSION_ON_LOGIN:
        login(request, user)
    return token


def token_logout(request):
    Token.objects.filter(user=request.user).delete()
    if settings.CREATE_SESSION_ON_LOGIN:
        logout(request)