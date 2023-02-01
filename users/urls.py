from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

User = get_user_model()
router = DefaultRouter()
router.register('', CustomUserViewSet)
urlpatterns = router.urls
