from unittest.mock import Mock, patch
import requests
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Concert, ConcertAttending


class BandWebsiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("listener", password="Concert-demo-2026!")
        cls.concert = Concert.objects.create(concert_name="Capstone Live", duration=2, city="Toronto")

    def test_home_page(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)

    def test_signup_hashes_password_and_signs_in(self):
        response = self.client.post(reverse("signup"), {"username": "newlistener", "password": "New-listener-2026!"})
        self.assertRedirects(response, reverse("index"))
        user = User.objects.get(username="newlistener")
        self.assertTrue(user.check_password("New-listener-2026!"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_duplicate_signup_is_rejected(self):
        response = self.client.post(reverse("signup"), {"username": "listener", "password": "New-listener-2026!"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="listener").count(), 1)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_and_logout(self):
        self.assertRedirects(self.client.post(reverse("login"), {"username": "listener", "password": "Concert-demo-2026!"}), reverse("index"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.get(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_bad_password_does_not_sign_in(self):
        self.client.post(reverse("login"), {"username": "listener", "password": "wrong"})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_anonymous_concert_access_redirects_to_login(self):
        self.assertEqual(self.client.get(reverse("concerts")).status_code, 302)
        self.assertEqual(self.client.get(reverse("concert_detail", args=[self.concert.id])).status_code, 302)

    def test_rsvp_updates_instead_of_creating_duplicate(self):
        self.client.force_login(self.user)
        for choice in ("Attending", "Not Attending"):
            response = self.client.post(reverse("concert_attendee"), {"concert_id": self.concert.id, "attendee_choice": choice})
            self.assertRedirects(response, reverse("concerts"))
        self.assertEqual(ConcertAttending.objects.count(), 1)
        self.assertEqual(ConcertAttending.objects.get().attending, "Not Attending")

    def test_invalid_rsvp_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("concert_attendee"), {"concert_id": self.concert.id, "attendee_choice": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ConcertAttending.objects.exists())

    def test_missing_concert_returns_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("concert_detail", args=[99999])).status_code, 404)

    @patch("concert.views.req.get")
    def test_songs_are_loaded_from_service(self, get):
        get.return_value = Mock(json=lambda: [{"id": 1, "title": "Service Song", "lyrics": "Words"}])
        response = self.client.get(reverse("songs"))
        self.assertContains(response, "Service Song")
        get.assert_called_once()

    @patch("concert.views.req.get", side_effect=requests.ConnectionError)
    def test_unavailable_catalogue_is_reported(self, get):
        self.assertEqual(self.client.get(reverse("photos")).status_code, 503)
