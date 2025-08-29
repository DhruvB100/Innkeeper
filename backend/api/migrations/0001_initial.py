from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Node",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("url", models.URLField(unique=True)),
                ("username", models.CharField(blank=True, max_length=100)),
                ("password", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(blank=True, default="", max_length=255)),
                ("content", models.TextField()),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            ("text/plain", "Plain Text"),
                            ("text/markdown", "Markdown"),
                            ("image/png;base64", "PNG Image"),
                            ("image/jpeg;base64", "JPEG Image"),
                        ],
                        default="text/plain",
                        max_length=50,
                    ),
                ),
                ("categories", models.CharField(blank=True, default="", max_length=500)),
                (
                    "visibility",
                    models.CharField(
                        choices=[("PUBLIC", "Public"), ("FRIENDS", "Friends Only"), ("PRIVATE", "Private")],
                        default="PUBLIC",
                        max_length=20,
                    ),
                ),
                ("url", models.URLField(blank=True)),
                ("source", models.URLField(blank=True, null=True)),
                ("origin", models.URLField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="posts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="InboxItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "item_type",
                    models.CharField(
                        choices=[("post", "Post"), ("like", "Like"), ("comment", "Comment"), ("follow", "Follow Request")],
                        max_length=20,
                    ),
                ),
                ("content", models.JSONField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="inbox_items", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("content", models.TextField()),
                ("content_type", models.CharField(default="text/plain", max_length=50)),
                ("url", models.URLField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="comments", to=settings.AUTH_USER_MODEL)),
                ("post", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="comments", to="api.post")),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="likes", to=settings.AUTH_USER_MODEL)),
                ("comment", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name="likes", to="api.comment")),
                ("post", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name="likes", to="api.post")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(condition=models.Q(post__isnull=False), fields=("author", "post"), name="unique_post_like"),
                    models.UniqueConstraint(
                        condition=models.Q(comment__isnull=False), fields=("author", "comment"), name="unique_comment_like"
                    ),
                ]
            },
        ),
    ]

