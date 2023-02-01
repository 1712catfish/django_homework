## Installation

Follow the [Django Custom User Model Tutorial](https://testdriven.io/blog/django-custom-user-model/): 
1. Create virtual environment
2. Create new Django project
3. Create `CustomUser` (prefer `AbstractUser` to `AbstractBaseUser`)
4. Create `CustomUserManager` (**Note:** change name of `create_user` function to `create`)

Then create a `requirements.txt` file in root directory:
```text
django
djangorestframework
drf-yasg
djangorestframework_simplejwt
psycopg2 # For PostgresSQL
```

## First steps
For django authentication example, see [djoser repo](https://github.com/sunscrapers/djoser).

Create a `permissions.py` file in `users` directory then clone `CurrentUserOrAdmin` and `CurrentUserOrAdminOrReadOnly` permission classes from `djoser/permissions.py` 
```python
"""Cloned from djoser/permissions.py"""
class CurrentUserOrAdmin(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.pk == user.pk
```

Create a `constants.py` file in `users` directory then clone common error messages from `djoser/constants.py`
```python
"""Cloned from djoser/constants.py"""
class Messages(object):
    INVALID_CREDENTIALS_ERROR = _("Unable to log in with provided credentials.")
    INACTIVE_ACCOUNT_ERROR = _("User account is disabled.")
    ...
```

Create a `serializers.py` file in `users` directory then clone useful serializers from `djoser/serializers.py`. In this repo, `CurrentPasswordSerializer`, `PasswordSerializer`, and `SetPasswordSerializer` is cloned.

**Note:** add `User = get_user_model()` before serializer classes so Django use custom user model.


```python
User = get_user_model()

"""Cloned from djoser/serializers.py"""
class CurrentPasswordSerializer(serializers.Serializer):
    """Validate current password"""
    current_password = serializers.CharField(style={"input_type": "password"})
    ...

class NewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})
    ...

class CustomPasswordSerializer(CurrentPasswordSerializer, NewPasswordSerializer):
    pass
```

## Customizing the project

#### Edit `utils.py`
1. Create a `utils.py` file then clone useful functions from `djoser/utils.py`.
2. Clone `login_user` as `token_login`, `logout_user` as `token_logout`.
4. Remove unused code (session, mailing.)
5. Define `TOKEN_MODEL` explicitly.

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
For more details, see [restframework docs](https://www.django-rest-framework.org/tutorial/1-serialization/) and `users/serializers.py`.

#### Edit `viewsets.py`
1. Clone `UserViewSet` from `djoser/views.py` and rename to `CustomUserViewSet` (**Note:** add `Custom` to signal that code has been edited.)
2. Delete unused methods.
3. Match appropriate permissions to actions in `def get_permissions(self):`. Permissions should be set in the project level `settings.py`. However for small project, permissions can be defined right in the get_permissions(self) method. For example, see `users/views.py`.
4. Match serializers to actions in `def get_serializer_class(self):`. For example, see `users/views.py`.
5. Clone `def me(self, request, *args, **kwargs):` and change so that users action `DESTROY` does not delete, but deactivate their account instead (set `is_active` to False).
6. Clone `def set_password(self, request, *args, **kwargs):` to allow users to change password.

#### Edit app level `urls.py`
Add generic `urlpatterns`:
```python
User = get_user_model()
router = DefaultRouter()
router.register('', CustomUserViewSet)
urlpatterns = router.urls
```


#### Edit project level `urls.py`
1. Add `drf_yasg`'s `schema_view` to auto-generate `swagger` and `redoc` api docs.
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
**Note:** in larger projects, `public` and `permissions_classes` arguments should be customized.

2. Add `users`'s urls:
```python
path('users', include('users.urls')),
```

3. Add `rest_framework_simplejwt`'s urls:
```python
re_path(r"^jwt/create/?", TokenObtainPairView.as_view(), name="jwt-create"),
re_path(r"^jwt/refresh/?", TokenRefreshView.as_view(), name="jwt-refresh"),
re_path(r"^jwt/verify/?", TokenVerifyView.as_view(), name="jwt-verify"),
```

4. Add `swagger`'s and `redoc`'s urls:
```python
re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0)),
re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0)),
```

#### Edit `settings.py`
1. Add `'users'`, `'rest_framework_simplejwt'`, and `'drf_yasg'` to `INSTALLED_APP`
```python
INSTALLED_APPS = [
    ...
    'rest_framework_simplejwt',
    'drf_yasg',
    'users',
]
```
2. Set `rest_framework_simplejwt` as default authentication class:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

#### Run server and test using Postman.

**Note:** place access token in collection's `Authorization` > `Bearer Token` > `Token` then in request, set `Authorization` > `Inherit auth from parent`. 

**Note:** set variables in collection's `Variables`.

#### Connect to Postgres
1. Install and setup Postgres 
- [On Windows (via pgAdmin)](https://www.guru99.com/download-install-postgresql.html)
- [On Linux](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart)
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
**Note:** in larger projects, database access information `NAME, USER, PASSWORD` should be stored in environment variable.

**Note:** to look up postgres database username, open pgAdmin server's `Properties` tab.

**Note:** create database in pgAdmin if encounter error `FATAL:  database "myproject" does not exist`.
