from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Author
from api.models import Post, Comment, Like


class PostTests(APITestCase):
    """Tests for post CRUD operations"""

    def setUp(self):
        # Create an approved user
        self.user = Author.objects.create_user(
            username='poster',
            password='pass123',
            email='poster@test.com',
            is_approved=True
        )
        # Create another user
        self.other_user = Author.objects.create_user(
            username='other',
            password='pass123',
            email='other@test.com',
            is_approved=True
        )

        # Create a test post
        self.post = Post.objects.create(
            author=self.user,
            title='Test Post',
            content='This is test content',
            visibility='PUBLIC'
        )

    def test_list_posts_returns_public_posts(self):
        """GET /api/posts/ should return public posts"""
        url = reverse('post_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post_requires_auth(self):
        """Creating a post requires authentication"""
        url = reverse('post_list_create')
        response = self.client.post(url, {
            'content': 'New post',
            'visibility': 'PUBLIC'
        }, format='json')
        # Should be 401 unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_as_approved_user(self):
        """Approved users can create posts"""
        self.client.force_authenticate(user=self.user)
        url = reverse('post_list_create')
        data = {
            'title': 'My Post',
            'content': 'Post content here',
            'content_type': 'text/plain',
            'visibility': 'PUBLIC'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Post content here')
        self.assertEqual(response.data['author'], str(self.user.pk))

    def test_unapproved_user_cannot_post(self):
        """Users that haven't been approved can't create posts"""
        unapproved = Author.objects.create_user(
            username='unapproved',
            password='pass123',
            email='unapproved@test.com',
            is_approved=False
        )
        self.client.force_authenticate(user=unapproved)
        url = reverse('post_list_create')
        response = self.client.post(url, {
            'content': 'trying to post',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_post_detail(self):
        """GET /api/posts/<id>/ returns post details with comments"""
        url = reverse('post_detail', args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.post.pk))
        self.assertIn('comments', response.data)

    def test_delete_post_only_by_owner(self):
        """Only the post author can delete their post"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('post_detail', args=[self.post.pk])
        response = self.client.delete(url)
        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_post(self):
        """Author can delete their own post"""
        self.client.force_authenticate(user=self.user)
        url = reverse('post_detail', args=[self.post.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class LikeTests(APITestCase):
    """Tests for liking posts"""

    def setUp(self):
        self.user = Author.objects.create_user(
            username='liker',
            password='pass123',
            email='liker@test.com',
            is_approved=True
        )
        self.post_author = Author.objects.create_user(
            username='postauthor',
            password='pass123',
            email='pa@test.com',
            is_approved=True
        )
        self.post = Post.objects.create(
            author=self.post_author,
            content='Like me!',
            visibility='PUBLIC'
        )

    def test_like_a_post(self):
        """Can like a post"""
        self.client.force_authenticate(user=self.user)
        url = reverse('post_like', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertTrue(Like.objects.filter(author=self.user, post=self.post).exists())

    def test_unlike_a_post(self):
        """Liking a post you already liked should unlike it"""
        Like.objects.create(author=self.user, post=self.post)
        self.client.force_authenticate(user=self.user)
        url = reverse('post_like', args=[self.post.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertFalse(Like.objects.filter(author=self.user, post=self.post).exists())


class CommentTests(APITestCase):
    """Tests for commenting on posts"""

    def setUp(self):
        self.user = Author.objects.create_user(
            username='commenter',
            password='pass123',
            email='commenter@test.com',
            is_approved=True
        )
        self.post = Post.objects.create(
            author=self.user,
            content='Comment on this!',
            visibility='PUBLIC'
        )

    def test_add_comment(self):
        """Can add a comment to a post"""
        self.client.force_authenticate(user=self.user)
        url = reverse('comment_list_create', args=[self.post.pk])
        response = self.client.post(url, {
            'content': 'Nice post!',
            'content_type': 'text/plain'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 1)

    def test_list_comments(self):
        """Can get all comments on a post"""
        Comment.objects.create(author=self.user, post=self.post, content='Comment 1')
        Comment.objects.create(author=self.user, post=self.post, content='Comment 2')

        url = reverse('comment_list_create', args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InboxTests(APITestCase):
    """Tests for federation inbox"""

    def setUp(self):
        self.user = Author.objects.create_user(
            username='inboxuser',
            password='pass123',
            email='inbox@test.com',
            is_approved=True
        )

    def test_get_inbox_requires_auth(self):
        """Can't access someone else's inbox"""
        url = reverse('inbox', args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_to_inbox_is_public(self):
        """Remote nodes should be able to POST to inbox without auth"""
        url = reverse('inbox', args=[self.user.pk])
        data = {
            'type': 'post',
            'content': 'Hello from remote node',
            'author': {'username': 'remoteuser'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_can_view_inbox(self):
        """Author can view their own inbox"""
        self.client.force_authenticate(user=self.user)
        url = reverse('inbox', args=[self.user.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'inbox')
