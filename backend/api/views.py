from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Post, Comment, Like, InboxItem, Node
from .serializers import (
    PostSerializer, PostDetailSerializer, CommentSerializer,
    LikeSerializer, InboxItemSerializer, NodeSerializer
)
from .permissions import IsAuthorOrReadOnly, IsApprovedUser, IsAdminOrReadOnly
from .federation import send_to_remote_inbox
from users.models import Author, Follow
from users.serializers import AuthorSerializer


class PostListCreateView(generics.ListCreateAPIView):
    """
    GET /api/posts/ - Get all public posts
    POST /api/posts/ - Create a new post
    """
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['visibility', 'content_type']
    search_fields = ['title', 'content', 'categories']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Return public posts, or posts visible to the logged in user
        if self.request.user.is_authenticated:
            # Show public posts + friend posts from people they follow
            following_ids = Follow.objects.filter(
                follower=self.request.user,
                is_accepted=True
            ).values_list('following_id', flat=True)

            from django.db.models import Q
            return Post.objects.filter(
                Q(visibility='PUBLIC') |
                Q(visibility='FRIENDS', author_id__in=following_ids) |
                Q(author=self.request.user)
            ).select_related('author')
        else:
            return Post.objects.filter(visibility='PUBLIC').select_related('author')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsApprovedUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # After creating a post, send it to followers' inboxes
        self._distribute_post_to_followers(post)

    def _distribute_post_to_followers(self, post):
        """
        Send the new post to all followers' inboxes.
        This is how federation works - we push to inboxes.
        """
        followers = Follow.objects.filter(
            following=self.request.user,
            is_accepted=True
        ).select_related('follower')

        post_data = PostSerializer(post, context={'request': self.request}).data

        for follow in followers:
            follower = follow.follower
            if follower.is_remote:
                # Send to remote node's inbox using the federation module
                success = send_to_remote_inbox(follower.url, post_data)
                if not success:
                    # Log it but don't fail the whole request
                    print(f"Warning: Failed to send post to remote inbox for {follower.username}")
            else:
                # Local follower - just create an inbox item directly
                InboxItem.objects.create(
                    author=follower,
                    item_type='post',
                    content=post_data
                )


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/posts/<id>/ - Get a specific post
    PUT /api/posts/<id>/ - Update a post
    DELETE /api/posts/<id>/ - Delete a post
    """
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]


class AuthorPostListView(generics.ListAPIView):
    """GET /api/authors/<author_id>/posts/ - Get all posts by a specific author"""
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        # Only public posts for authors we're not following
        if self.request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=self.request.user,
                following_id=author_id,
                is_accepted=True
            ).exists()

            if is_following or str(self.request.user.pk) == str(author_id):
                return Post.objects.filter(author_id=author_id).exclude(visibility='PRIVATE')

        return Post.objects.filter(author_id=author_id, visibility='PUBLIC')


class LikePostView(APIView):
    """
    POST /api/posts/<id>/like/ - Like or unlike a post
    """
    permission_classes = [permissions.IsAuthenticated, IsApprovedUser]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        existing_like = Like.objects.filter(author=request.user, post=post).first()
        if existing_like:
            # Already liked - unlike it
            existing_like.delete()
            return Response({'message': 'Post unliked', 'liked': False})
        else:
            # Like the post
            Like.objects.create(author=request.user, post=post)

            # Send like to post author's inbox
            if post.author != request.user:
                like_data = {
                    'type': 'Like',
                    'author': AuthorSerializer(request.user).data,
                    'object': str(post.url)
                }
                InboxItem.objects.create(
                    author=post.author,
                    item_type='like',
                    content=like_data
                )

            return Response({'message': 'Post liked', 'liked': True})


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET /api/posts/<post_id>/comments/ - Get comments for a post
    POST /api/posts/<post_id>/comments/ - Add a comment to a post
    """
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id']).select_related('author')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsApprovedUser()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = serializer.save(author=self.request.user, post=post)

        # Send comment notification to post author's inbox
        if post.author != self.request.user:
            comment_data = CommentSerializer(comment, context={'request': self.request}).data
            InboxItem.objects.create(
                author=post.author,
                item_type='comment',
                content=comment_data
            )


class InboxView(APIView):
    """
    GET /api/authors/<id>/inbox/ - Get inbox items for an author
    POST /api/authors/<id>/inbox/ - Add item to inbox (used by remote nodes for federation)
    DELETE /api/authors/<id>/inbox/ - Clear inbox
    """

    def get_permissions(self):
        # Remote nodes use basic auth to POST to inbox
        # But only the author can GET their inbox
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request, pk):
        # Only allow viewing your own inbox
        if str(request.user.pk) != str(pk):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        inbox_items = InboxItem.objects.filter(author_id=pk)
        serializer = InboxItemSerializer(inbox_items, many=True)

        return Response({
            'type': 'inbox',
            'author': f"{request.build_absolute_uri('/').rstrip('/')}//api/authors/{pk}",
            'items': serializer.data
        })

    def post(self, request, pk):
        """
        Remote nodes send items here.
        They can send posts, likes, comments, or follow requests.
        """
        author = get_object_or_404(Author, pk=pk)
        data = request.data

        item_type = data.get('type', '').lower()

        if item_type not in ['post', 'like', 'comment', 'follow']:
            return Response({'error': 'Invalid item type'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the inbox item
        InboxItem.objects.create(
            author=author,
            item_type=item_type,
            content=data
        )

        return Response({'message': 'Item added to inbox'}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Clear all items from inbox"""
        if str(request.user.pk) != str(pk):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        InboxItem.objects.filter(author_id=pk).delete()
        return Response({'message': 'Inbox cleared'})


class FeedView(APIView):
    """
    GET /api/feed/ - Get the personalized feed for the logged in user
    Shows posts from people you follow + your own posts
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get IDs of people we're following
        following_ids = Follow.objects.filter(
            follower=request.user,
            is_accepted=True
        ).values_list('following_id', flat=True)

        from django.db.models import Q
        posts = Post.objects.filter(
            Q(author=request.user) |
            Q(author_id__in=following_ids, visibility__in=['PUBLIC', 'FRIENDS'])
        ).select_related('author').order_by('-created_at').distinct()[:50]  # limit to 50 posts, distinct fixes duplicate issue

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class NodeListView(generics.ListCreateAPIView):
    """Admin only endpoint to manage remote nodes"""
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = [IsAdminOrReadOnly]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def node_info(request):
    """
    GET /api/
    Returns info about this node. Remote nodes use this to discover us.
    """
    from django.conf import settings
    return Response({
        'type': 'node',
        'name': settings.NODE_NAME,
        'url': settings.NODE_URL,
        'description': 'Innkeeper federated social platform node',
    })
