import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Author(AbstractUser):
    """
    Custom user model. I extended AbstractUser so we keep all the
    default django auth stuff but add our own fields.

    In the federated network each author has a unique URL that identifies them
    across nodes.
    """

    # Using UUID as primary key because it's unique across all nodes
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The display name shown on the platform
    display_name = models.CharField(max_length=100, blank=True)

    # Profile picture URL - could be remote or local
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Bio/about section
    bio = models.TextField(blank=True, default='')

    # GitHub profile link (optional)
    github = models.URLField(blank=True, null=True)

    # The full URL of this author on their node
    # Something like http://nodeurl.com/api/authors/uuid
    url = models.URLField(blank=True)

    # The host node this author belongs to
    host = models.URLField(blank=True)

    # Whether this is a local author or from a remote node
    is_remote = models.BooleanField(default=False)

    # Role based access - admins can approve/deny registrations
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('author', 'Author'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='author')

    # New accounts need admin approval before they can post
    # This is for the "node admin can approve new signups" requirement
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Auto-generate the URL based on the host and id
        if not self.host:
            self.host = settings.NODE_URL
        if not self.url and self.id:
            self.url = f"{self.host}/api/authors/{self.id}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class Follow(models.Model):
    """
    Represents a follow relationship between two authors.
    The follower follows the following_author.

    This works across nodes too - you can follow someone on another server.
    """

    # Who is doing the following
    follower = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='following_set'
    )

    # Who is being followed
    following = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='followers_set'
    )

    # Follow requests need to be accepted
    # TODO: implement the accept/reject flow properly
    is_accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Can't follow the same person twice
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
