from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model
from .serializers import UserProfileSerializer
from recipes.permissions import OwnerAdminReadOnly

User = get_user_model()


class NotDefaultUser(UserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserProfileSerializer
    permission_classes = [OwnerAdminReadOnly]
