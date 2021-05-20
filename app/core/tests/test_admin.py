from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):

    def setUp(self):

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'adminuser@testing.com',
            password='password123'
        )
        #loggin in the admin user to the test client
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'testuser@testing.com',
            password='testpassword',
            name = 'test user fullname',
        )


    def test_user_listed(self):
        """Test that users are listed on user page in admin site"""

        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response,self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """ Test that user edit page works"""
        url = reverse('admin:core_user_change',args=[self.user.id])
        res = self.client.get(url)

        self.assertEquals(res.status_code,200)

    def test_create_user_page(self):
        """ test that create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code,200)
