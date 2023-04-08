from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=(
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким username уже существует'),
        )
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=(
            RegexValidator(r'^[\w.@+-]+$', message='Проверьте username!'),
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует'
            )
        )
    )
    password = serializers.CharField(
        max_length=150, write_only=True
    )

    """Сериализатор регистрации пользователя."""
    class Meta(UserCreateSerializer.Meta):
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password',)
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор авторизованного пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        """Метод определяет подписан ли текущий пользователь на автора."""
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and obj.subscribed.filter(user=user).exists()
        )
