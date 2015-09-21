from django.conf.urls import url, include
from rest_framework import routers
from .views import UserViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, base_name='user')

urlpatterns = router.urls
