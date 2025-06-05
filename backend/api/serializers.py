from rest_framework import serializers
from .models import Post, Comment, Like, InboxItem, Node
from users.serializers import AuthorSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""

    author_info = AuthorSerializer(source='author', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_info', 'content', 'content_type', 'url', 'created_at']
        read_only_fields = ['id', 'author', 'url', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for likes"""

    author_info = AuthorSerializer(source='author', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'author', 'author_info', 'post', 'comment', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """
    Main serializer for posts.
    Includes author info, comment count, like count.
    """

    author_info = AuthorSerializer(source='author', read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    # Whether the current user has liked this post
    user_has_liked = serializers.SerializerMethodField()
    # Include the categories as a list for easier frontend use
    categories_list = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_info', 'title', 'content',
            'content_type', 'categories', 'categories_list',
            'visibility', 'url', 'source', 'origin',
            'comments_count', 'likes_count', 'user_has_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'url', 'created_at', 'updated_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user_has_liked(self, obj):
        # Check if the current user has liked this post
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(author=request.user).exists()
        return False

    def get_categories_list(self, obj):
        # Split categories string into list
        if obj.categories:
            return [c.strip() for c in obj.categories.split(',') if c.strip()]
        return []


class PostDetailSerializer(PostSerializer):
    """
    More detailed post serializer that includes the actual comments.
    Using a separate serializer to avoid loading all comments when just listing posts.
    """

    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments', 'likes']


class InboxItemSerializer(serializers.ModelSerializer):
    """Serializer for inbox items"""

    class Meta:
        model = InboxItem
        fields = ['id', 'author', 'item_type', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class NodeSerializer(serializers.ModelSerializer):
    """Serializer for remote nodes"""

    class Meta:
        model = Node
        fields = ['id', 'name', 'url', 'username', 'is_active', 'created_at']
        # Don't expose password in the API
        extra_kwargs = {
            'password': {'write_only': True}
        }
