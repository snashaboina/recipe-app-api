from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='test123'
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='user@gmail.com',
            password='test123',
            name='normal user'
        )

    def test_users_listed(self):
        """
        Test whether the created users listed on the user page
        """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        """
        Tests whether the user edit page shows up with status_code 200
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)

    def test_user_add_page(self):
        """
        Tests whether
        """
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEquals(res.status_code, 200)
