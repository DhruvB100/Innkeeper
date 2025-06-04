from django.contrib import admin
from .models import Post, Comment, Like, InboxItem, Node


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'visibility', 'content_type', 'created_at']
    list_filter = ['visibility', 'content_type']
    search_fields = ['title', 'content', 'author__username']
    ordering = ['-created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    ordering = ['-created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'comment', 'created_at']


@admin.register(InboxItem)
class InboxItemAdmin(admin.ModelAdmin):
    list_display = ['author', 'item_type', 'is_read', 'created_at']
    list_filter = ['item_type', 'is_read']
    ordering = ['-created_at']


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_at']
    list_filter = ['is_active']
