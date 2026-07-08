from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .serializers import LoginSerializer, SignupSerializer


class LoginThrottle(ScopedRateThrottle):
    """Per the client's IP address, independent of the shared anon rate,
    so login/signup guessing is limited even if other endpoints are busy.

    IMPORTANT: DRF's ScopedRateThrottle reads its scope from a
    `throttle_scope` attribute on the *view* (see allow_request(), which does
    `self.scope = getattr(view, 'throttle_scope', None)`), not from an
    attribute set on this throttle subclass. Setting `scope = 'login'` here
    does nothing by itself — every view that uses this throttle MUST also
    define `throttle_scope = 'login'`, or the throttle silently allows every
    request (no rate limiting at all)."""


def _user_payload(user, token):
    return {
        'token': token.key,
        'name': user.first_name or user.username,
        'phone': user.username,
        'is_staff': user.is_staff,
    }


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]
    throttle_scope = 'login'

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response(_user_payload(user, token), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    Single login endpoint used by both regular customers and the store admin.
    The frontend can check the returned `is_staff` flag to decide whether to
    show the admin panel (create an admin user with `createsuperuser`).
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]
    throttle_scope = 'login'

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        user = authenticate(request, username=phone, password=password)
        if user is None:
            return Response({'detail': 'شماره یا رمز عبور اشتباه است'}, status=status.HTTP_401_UNAUTHORIZED)
        token, _created = Token.objects.get_or_create(user=user)
        return Response(_user_payload(user, token))


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'name': request.user.first_name or request.user.username,
            'phone': request.user.username,
            'is_staff': request.user.is_staff,
        })
