## Installation

See the [Django Custom User Model Tutorial](https://testdriven.io/blog/django-custom-user-model/) to 
1. Create virtual environment
2. Create new Django project
3. Create `CustomUser` (prefer `AbstractUser` to `AbstractBaseUser`)
4. Create `CustomUserManager` (**Note:** Change name of `create_user` function to `create`)

Then create a `requirements.txt` file in root directory:
```text
django
djangorestframework
drf-yasg
djangorestframework_simplejwt
psycopg2 # For PostgresSQL
```

## Clone boilerplate code
Access [djoser](https://github.com/sunscrapers/djoser) to clone common code.

### In `users` directory

Create a `permissions.py` file then clone `CurrentUserOrAdmin` and `CurrentUserOrAdminOrReadOnly` permission classes from `djoser/permissions.py` 
```python
"""Cloned from djoser/permissions.py"""

from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class CurrentUserOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.pk == user.pk


class CurrentUserOrAdminOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if type(obj) == type(user) and obj == user:
            return True
        return request.method in SAFE_METHODS or user.is_staff
```

Create a `constants.py` file then clone common error messages from `djoser/constants.py`
```python
"""Cloned from djoser/constants.py"""

from django.utils.translation import gettext_lazy as _


class Messages(object):
    INVALID_CREDENTIALS_ERROR = _("Unable to log in with provided credentials.")
    INACTIVE_ACCOUNT_ERROR = _("User account is disabled.")
    INVALID_TOKEN_ERROR = _("Invalid token for given user.")
    INVALID_UID_ERROR = _("Invalid user id or user doesn't exist.")
    STALE_TOKEN_ERROR = _("Stale token for given user.")
    PASSWORD_MISMATCH_ERROR = _("The two password fields didn't match.")
    USERNAME_MISMATCH_ERROR = _("The two {0} fields didn't match.")
    INVALID_PASSWORD_ERROR = _("Invalid password.")
    EMAIL_NOT_FOUND = _("User with given email does not exist.")
    CANNOT_CREATE_USER_ERROR = _("Unable to create account.")
```

Create a `serializers.py` file then clone useful serializers from `djoser/serializers.py`. In this repo, `CurrentPasswordSerializer`, `PasswordSerializer`, and `SetPasswordSerializer` is cloned.

**Note:** add `User = get_user_model()` before serializer classes so Django use custom user model


```python
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


class NewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user = self.context["request"].user or self.user
        # why assert? There are ValidationError / fail everywhere
        assert user is not None
        validate_password(attrs["new_password"], user)
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"details": "New password is the same as old password!"})
        return super().validate(attrs)


class CustomPasswordSerializer(CurrentPasswordSerializer, NewPasswordSerializer):
    pass
```

### Customize code to project

#### Edit `utils.py`
1. Create a `utils.py` file then clone useful functions from `djoser/utils.py`
2. `login_user` is cloned as `token_login`
3. `logout_user` is cloned as `token_logout`
4. Code to handle session and mailing is removed
5. `TOKEN_MODEL` is defined explicitly.

For more details, see `users/utils.py`.


#### Edit `serializers.py`:

1. Create additional serializer for each viewset in this format:
```python
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = database_table
        fields = (allowed_access_table_field_1, allowed_access_table_field_2,...)
        read_only_fields = (read_only_field_1, read_only_field_2,)
```
Explaination: Django allow users to access defined `fields` of the `User` model (database table). 
`read_only_fields` defines fields that can only be read.


#### Edit `viewsets.py`
1. Clone `UserViewSet` from `djoser/views.py` and rename `CustomUserViewSet` (add `Custom` to signal that code has been edited.)
2. Delete unused methods.
3. Edit `def get_permissions(self):` to match permissions with actions. Permissions should be set in the project level `settings.py`. However for small project, permissions can be set right in the get_permissions(self) method. For example, see `users/views.py`.
4. Edit `def get_serializer_class(self):` to match serializers with actions. For example, see `users/views.py`.
5. In this repo, `def me(self, request, *args, **kwargs):` is changed so that users action `DESTROY` does not delete their account, but deactivate their account (set `is_active` to False) instead.
6. Clone `def set_password(self, request, *args, **kwargs):` for users to change password.

#### Edit app level `urls.py`
1. Add `urlpatterns` from viewset:
```python
User = get_user_model()
router = DefaultRouter()
router.register('', CustomUserViewSet)
urlpatterns = router.urls

```


#### Edit project level `urls.py`
1. Add `drf_yasg`'s `schema_view` for autogenerated `swagger` and `redoc` api docs.
```python
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)
```
**In large projects, `public` and `permissions_classes` arguments should be customized.**

2. Add `users` urls:
```python
path('users', include('users.urls')),
```

3. Add `rest_framework_simplejwt` urls:
```python
re_path(r"^jwt/create/?", TokenObtainPairView.as_view(), name="jwt-create"),
re_path(r"^jwt/refresh/?", TokenRefreshView.as_view(), name="jwt-refresh"),
re_path(r"^jwt/verify/?", TokenVerifyView.as_view(), name="jwt-verify"),
```

4. Add `swagger` and `redoc` urls:
```python
re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0)),
re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0)),
```

#### Edit `settings.py`
1. Add `'users'`, `'rest_framework_simplejwt'`, and `'drf_yasg'` to `INSTALLED_APP`
2. Set `rest_framework_simplejwt` as default authentication class:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

#### Run and test server using Postman.
#### Connect to Postgres
1. Install and setup Postgres
2. Configure the Django database settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myproject',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
**Note:** In production, database access information `NAME, USER, PASSWORD` should be stored in environment variable.

**Note:** Look up postgres database owner in server's `Properties` tab.

**Note:** Create database in pgAdmin if encounter error `FATAL:  datab
ase "myproject" does not exist`

#### Save to Github
