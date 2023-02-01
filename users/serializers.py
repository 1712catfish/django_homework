from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .constants import Messages

User = get_user_model()


class CurrentPasswordSerializer(serializers.Serializer):
    """Validate current password"""
    current_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "invalid_password": Messages.INVALID_PASSWORD_ERROR
    }

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail("invalid_password")


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = self.context["request"].user or self.user
        # why assert? There are ValidationError / fail everywhere
        assert user is not None
        validate_password(attrs["new_password"], user)
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"details": "New password is the same as old password!"})
        return super().validate(attrs)


class SetPasswordSerializer(CurrentPasswordSerializer, PasswordSerializer):
    pass


class CustomAdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email',)


class CustomAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'name', 'phone', 'birth_date',)
        read_only_fields = ('email',)


class CustomUserCreateSerializer(serializers.ModelSerializer):
    default_error_messages = {
        "cannot_create_user": Messages.CANNOT_CREATE_USER_ERROR
    }

    class Meta:
        model = User
        fields = ('email', 'username', 'name', 'phone', 'birth_date', 'password',)
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CustomUserDeleteSerializer(
    CurrentPasswordSerializer,  # In order to delete account, user has to enter password
    serializers.ModelSerializer,
):
    class Meta:
        model = User
        fields = ('password', 'is_active',)
        read_only_fields = ('password',)
