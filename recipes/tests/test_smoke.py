from django.test import TestCase, Client
from django.urls import reverse

class SmokeTests(TestCase):
    def test_healthcheck(self):
        # basic sanity to prove test runner works
        self.assertTrue(True)

    def test_home_page_loads(self):
        client = Client()
        url = reverse("recipes:home")  # adjust if your url name differs
        resp = client.get(url)
        self.assertEqual(resp.status_code, 200)