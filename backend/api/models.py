import uuid
from django.db import models
from django.conf import settings


class Post(models.Model):
    """
    A post made by an author. Posts can be public or private.
    They can also be shared from remote nodes.
    """

    # Post types - we support plain text and markdown
    CONTENT_TYPE_CHOICES = [
        ('text/plain', 'Plain Text'),
        ('text/markdown', 'Markdown'),
        ('image/png;base64', 'PNG Image'),
        ('image/jpeg;base64', 'JPEG Image'),
    ]

    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public'),
        ('FRIENDS', 'Friends Only'),
        ('PRIVATE', 'Private'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The author who wrote this post
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField()
    content_type = models.CharField(
        max_length=50,
        choices=CONTENT_TYPE_CHOICES,
        default='text/plain'
    )

    # Tags are stored as comma separated string for simplicity
    # could use a ManyToMany but this is easier for now
    categories = models.CharField(max_length=500, blank=True, default='')

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='PUBLIC'
    )

    # The URL of this post (for federation)
    url = models.URLField(blank=True)

    # For remote posts shared from another node
    source = models.URLField(blank=True, null=True)
    origin = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.title or self.content[:50]}"

    def save(self, *args, **kwargs):
        if not self.url and self.id:
            self.url = f"{settings.NODE_URL}/api/authors/{self.author.id}/posts/{self.id}"
        super().save(*args, **kwargs)

    def get_likes_count(self):
        return self.likes.count()


class Comment(models.Model):
    """Comments on posts"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The post this comment is on
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    # Who wrote the comment
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.TextField()
    content_type = models.CharField(max_length=50, default='text/plain')

    # URL of this comment (for federation)
    url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # show oldest comments first

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


class Like(models.Model):
    """
    Likes on posts or comments.
    An author can only like a post once.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    # A like can be on either a post or a comment
    # Using generic FK would be cleaner but this is simpler
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Can't like the same post twice
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_post_like'
            ),
            models.UniqueConstraint(
                fields=['author', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_comment_like'
            ),
        ]

    def __str__(self):
        target = self.post or self.comment
        return f"{self.author.username} liked {target}"


class InboxItem(models.Model):
    """
    The inbox stores items sent to an author from other nodes.
    Remote nodes POST to /api/authors/<id>/inbox/ to deliver content.

    This is how federation works - remote servers push content here.
    """

    ITEM_TYPE_CHOICES = [
        ('post', 'Post'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow Request'),
    ]

    # Who this inbox item is for
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inbox_items'
    )

    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)

    # Store the raw JSON from the remote node
    # We store it as-is because different nodes might send slightly different formats
    content = models.JSONField()

    # Whether the user has read this
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inbox item ({self.item_type}) for {self.author.username}"


class Node(models.Model):
    """
    Represents a remote Innkeeper node that we can federate with.
    Node admins need to add remote nodes and configure credentials.
    """

    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)

    # Credentials for authenticating with the remote node
    # They give us a username/password to use
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)  # TODO: should encrypt this

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.url})"
