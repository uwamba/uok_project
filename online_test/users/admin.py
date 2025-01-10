from django.contrib import admin
from .models import Candidate, Admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Candidate, Admin


admin.site.register(Admin)
admin.site.register(Candidate)


# Customize UserAdmin to display role-based fields
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_admin', 'is_candidate', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_candidate', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Roles', {'fields': ('is_admin', 'is_candidate')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'is_candidate', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

# Register your models
admin.site.register(User, CustomUserAdmin)

class CustomUserAdmin(UserAdmin):
    ...
    
    def has_module_permission(self, request, obj=None):
        if request.user.is_admin:
            return True  # Admins see everything
        elif request.user.is_candidate:
            return False  # Candidates don't see the admin dashboard
        return super().has_module_permission(request, obj)

