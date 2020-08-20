from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='sampleuser@gmail.com', password="testpassword"):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email is successful
        """
        email = "test@gmail.com"
        password = "Test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_normalize_email(self):
        """
        Testing whether the email gets normalized on the user creation or not
        """
        email = 'person@DJANGO.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_create_user_invalid_email(self):
        """
        Test whether the create_user function raise error
        when invalid email passed
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """
        Tests a user is a super user and staff when created
        through create_superuser function
        """
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_model_str_representation(self):
        """
        Test whether the name is the string representation of tag model
        """
        tag = models.Tag.objects.create(user=sample_user(), name="vegan")

        self.assertEqual(str(tag), tag.name)
