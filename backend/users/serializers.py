from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from recipes.models import Subscribes
from rest_framework import serializers

User = get_user_model()


class LoginUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']

        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(UserSerializer):
    '''Сериализатор для регистрации просмотра профайла пользователя
        действует на все endpoint's with user/..'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """проверка поля is_subscribed на наличие подписок"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribes.objects.filter(user=request.user,
                                         following=obj.id).exists()


class CurrentUserProfileSerializer(UserSerializer):
    '''Сериализатор для просмотра текущего пользователя
        users/me'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['username'] = self.context['username']
        return attrs

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribes.objects.filter(user=request.user,
                                         following=obj.id).exists()
