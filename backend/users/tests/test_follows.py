"""
Tests for the follow/unfollow functionality.
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import Author, Follow


class FollowTests(APITestCase):

    def setUp(self):
        self.user_a = Author.objects.create_user(
            username='user_a', password='pass123',
            email='a@test.com', is_approved=True
        )
        self.user_b = Author.objects.create_user(
            username='user_b', password='pass123',
            email='b@test.com', is_approved=True
        )

    def test_can_follow_another_user(self):
        """Should be able to send a follow request"""
        self.client.force_authenticate(user=self.user_a)
        url = reverse('follow', args=[self.user_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(
            follower=self.user_a,
            following=self.user_b
        ).exists())

    def test_cannot_follow_yourself(self):
        """Users shouldn't be able to follow themselves"""
        self.client.force_authenticate(user=self.user_a)
        url = reverse('follow', args=[self.user_a.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_follow_same_person_twice(self):
        """Following the same person twice should return an error"""
        Follow.objects.create(
            follower=self.user_a,
            following=self.user_b
        )
        self.client.force_authenticate(user=self.user_a)
        url = reverse('follow', args=[self.user_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_unfollow(self):
        """Should be able to unfollow someone"""
        Follow.objects.create(
            follower=self.user_a,
            following=self.user_b,
            is_accepted=True
        )
        self.client.force_authenticate(user=self.user_a)
        url = reverse('follow', args=[self.user_b.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Follow.objects.filter(
            follower=self.user_a,
            following=self.user_b
        ).exists())

    def test_follow_requires_authentication(self):
        """Anonymous users can't follow people"""
        url = reverse('follow', args=[self.user_b.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accept_follow_request(self):
        """Author can accept a follow request"""
        follow = Follow.objects.create(
            follower=self.user_a,
            following=self.user_b,
            is_accepted=False
        )
        self.client.force_authenticate(user=self.user_b)
        url = reverse('accept_follow', args=[self.user_b.pk, self.user_a.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        follow.refresh_from_db()
        self.assertTrue(follow.is_accepted)

    def test_only_followee_can_accept(self):
        """Only the person being followed can accept the request"""
        Follow.objects.create(
            follower=self.user_a,
            following=self.user_b,
            is_accepted=False
        )
        # user_a tries to accept their own request (shouldn't work)
        self.client.force_authenticate(user=self.user_a)
        url = reverse('accept_follow', args=[self.user_b.pk, self.user_a.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
