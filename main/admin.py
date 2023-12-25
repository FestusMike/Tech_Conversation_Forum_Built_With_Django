from django.contrib import admin
from .models import Room, Topic, Message, User
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('avatar', 'bio',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('avatar', 'bio',)}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Topic)
admin.site.register(Room)
admin.site.register(Message)