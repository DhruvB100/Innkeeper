from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Author, Follow


class AuthorAdmin(UserAdmin):
    """Custom admin for Author model"""
    list_display = ['username', 'email', 'display_name', 'role', 'is_approved', 'is_remote', 'created_at']
    list_filter = ['is_approved', 'role', 'is_remote']
    search_fields = ['username', 'email', 'display_name']
    ordering = ['-created_at']

    # Add our custom fields to the admin edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Innkeeper Profile', {
            'fields': ('display_name', 'bio', 'profile_image', 'github', 'url', 'host', 'is_remote', 'role', 'is_approved')
        }),
    )

    # Actions for bulk approving users
    actions = ['approve_authors']

    def approve_authors(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} authors approved')
    approve_authors.short_description = 'Approve selected authors'


admin.site.register(Author, AuthorAdmin)
admin.site.register(Follow)
