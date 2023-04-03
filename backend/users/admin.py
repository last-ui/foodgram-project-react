from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from users.models import Subscribe, User


class UserCreateForm(UserCreationForm):
    """Кастомная форма создания пользователя в админ-зоне."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserCreateForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                ('is_active',),
                ('username', 'email', 'password1',),
                ('first_name', 'last_name',),)
        }),
    )
    list_display = (
        'username', 'first_name', 'last_name', 'email', 'is_active',
    )
    fields = (
        ('is_active',),
        ('username', 'email', 'password',),
        ('first_name', 'last_name',),
    )
    fieldsets = []

    search_fields = (
        'username', 'email',
    )
    list_filter = (
        'is_active', 'first_name', 'email',
    )


admin.site.site_header = 'Foodgram - администрирование'
admin.site.register(Subscribe)
