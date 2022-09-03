from django.urls import path, include, re_path
from .views import NotDefaultUser
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'users', NotDefaultUser)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]
