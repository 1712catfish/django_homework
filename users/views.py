from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .permissions import CurrentUserOrAdmin
from .serializers import CustomAdminSerializer, CustomAdminListSerializer, CustomUserSerializer, \
    CustomUserDeleteSerializer, SetPasswordSerializer, CustomUserCreateSerializer
from .utils import token_logout

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminUser, ]

    def get_instance(self):
        return self.request.user

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny, ]
        elif self.action == "list":
            self.permission_classes = [IsAdminUser, ]
        elif self.action == "me":
            self.permission_classes = [CurrentUserOrAdmin, ]
        elif self.action in ["reset_password", ]:
            self.permission_classes = [CurrentUserOrAdmin, ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        if self.request.user.is_staff:
            if self.request.method == "GET" and self.kwargs.get("pk") is None:
                return CustomAdminListSerializer
            return CustomAdminSerializer
        if self.action == "me":
            if self.request.method == "DELETE":
                return CustomUserDeleteSerializer
            return CustomUserSerializer
        if self.action == "reset_password":
            return SetPasswordSerializer
        return self.serializer_class

    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            instance = self.get_object()
            instance.is_active = False
            instance.save(update_fields=["is_active"])

            token_logout(request)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()
        instance.set_password(serializer.validated_data.get('new_password'))
        instance.save()

        token_logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)
