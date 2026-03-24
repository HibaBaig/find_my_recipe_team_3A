from django.test import TestCase, Client
from django.urls import reverse

class SmokeTests(TestCase):
    def test_healthcheck(self):
        self.assertTrue(True)

    def test_home_page_loads(self):
        client = Client()
        resp = client.get(reverse("recipes:home"))  # adjust url name if different
        self.assertEqual(resp.status_code, 200)