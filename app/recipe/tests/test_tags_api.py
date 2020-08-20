from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
from recipe.serializers import TagSerializers



TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_user_cannot_retrieve_tags(self):
        """Test checks that un authenticated user cannot retrieve tags"""
        res = self.client.get(TAGS_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):

    def setUp(self):
        """Creating a user and authenticating to that we can create tags"""
        self.user = get_user_model().objects.create_user(
            email='tagtestuser@gmail.com',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_tags_retrival_autenticated_user(self):
        """Tests that authenticated user can retrieve tags"""
        tag1 = Tag.objects.create(
            user=self.user,
            name='Lunch'
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name='Dessert'
        )

        res = self.client.get(TAGS_URL)
        serializer = TagSerializers(Tag.objects.all().order_by('-name'), many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_only_authorized_user_tags_retrieved(self):
        """test that api only retrieves authorized user tags"""
        other_user = get_user_model().objects.create_user(
            email='othertagtestuser@gmail.com',
            password='testpassword2'
        )
        tag1 = Tag.objects.create(
            user=other_user,
            name='Lunch'
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name='Dessert'
        )

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], tag2.name)
        self.assertEqual(len(res.data), 1)
