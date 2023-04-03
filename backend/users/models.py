from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс для создания модели пользователя."""

    first_name = models.CharField(
        'Имя',
        max_length=150,
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    REQUIRED_FIELDS = ('first_name', 'last_name')
    USERNAME_FIELDS = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribed",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscribed"
            ),
        ]

    def __str__(self):
        return f'{self.user} subscribed {self.author}'
