from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from mailings.models import Mailing


class MailingTestCase(APITestCase):
    """Тесты для модели Mailing."""

    def setUp(self):
        self.mailing = Mailing.objects.create(email="test@example.com", mailing=True)

    def test_mailing_retrieve(self):
        """Тест проверки просмотра подписки."""
        url = reverse("mailings:mailings-detail", args=(self.mailing.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("email"), "test@example.com")
        self.assertTrue(data.get("mailing"))

    def test_mailings_list(self):
        """Тест проверки просмотра списка подписок."""
        url = reverse("mailings:mailings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mailing_create(self):
        """Тест проверки создания подписки методом POST."""
        url = reverse("mailings:mailings-list")
        data = {"email": "new@example.com", "mailing": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Mailing.objects.count(), 2)
        self.assertEqual(response.data["message"], "Спасибо за подписку!")

    def test_mailing_create_without_mailing_field(self):
        """Тест проверки создания подписки без указания mailing (должно быть True по умолчанию)."""
        url = reverse("mailings:mailings-list")
        data = {"email": "default@example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mailing = Mailing.objects.get(email="default@example.com")
        self.assertTrue(mailing.mailing)

    def test_mailing_update_put(self):
        """Тест проверки полного обновления подписки методом PUT."""
        url = reverse("mailings:mailings-detail", args=(self.mailing.pk,))
        data = {"email": "updated@example.com", "mailing": False}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mailing.refresh_from_db()
        self.assertEqual(self.mailing.email, "updated@example.com")
        self.assertFalse(self.mailing.mailing)

    def test_mailing_update_patch(self):
        """Тест проверки частичного обновления подписки методом PATCH."""
        url = reverse("mailings:mailings-detail", args=(self.mailing.pk,))
        data = {"mailing": False}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mailing.refresh_from_db()
        self.assertFalse(self.mailing.mailing)
        self.assertEqual(self.mailing.email, "test@example.com")

    def test_mailing_delete(self):
        """Тест проверки удаления подписки (мягкое удаление - mailing=False)."""
        url = reverse("mailings:mailings-detail", args=(self.mailing.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.mailing.refresh_from_db()
        self.assertFalse(self.mailing.mailing)
        self.assertEqual(Mailing.objects.count(), 1)

    def test_invalid_email(self):
        """Тест проверки невалидного email при создании."""
        url = reverse("mailings:mailings-list")
        data = {"email": "invalid-email", "mailing": True}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
