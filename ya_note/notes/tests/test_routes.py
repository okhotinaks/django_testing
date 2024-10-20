from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()

LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
HOME_URL = reverse('notes:home')
ADD_URL = reverse('notes:add')
LIST_URL = reverse('notes:list')
SUCCESS_URL = reverse('notes:success')


def detail_url(slug):
    return reverse('notes:detail', args=(slug,))


def edit_url(slug):
    return reverse('notes:edit', args=(slug,))


def delete_url(slug):
    return reverse('notes:delete', args=(slug,))


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Охотина Ксения')
        cls.reader = User.objects.create(username='Читатель')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-note',
            author=cls.author,
        )

    def test_pages_availability_for_different_user(self):
        urls = (
            (detail_url(self.note.slug), HTTPStatus.FOUND),
            (edit_url(self.note.slug), HTTPStatus.FOUND),
            (delete_url(self.note.slug), HTTPStatus.FOUND),
            (ADD_URL, HTTPStatus.FOUND),
            (SUCCESS_URL, HTTPStatus.FOUND),
            (LIST_URL, HTTPStatus.FOUND),
            (HOME_URL, HTTPStatus.OK),
            (LOGIN_URL, HTTPStatus.OK),
            (LOGOUT_URL, HTTPStatus.OK),
            (SIGNUP_URL, HTTPStatus.OK),
        )
        for url, expected_status in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            (detail_url(self.note.slug),),
            (edit_url(self.note.slug),),
            (delete_url(self.note.slug),),
            (ADD_URL,),
            (SUCCESS_URL,),
            (LIST_URL,),
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{LOGIN_URL}?next={url[0]}'
                response = self.client.get(url[0])
                self.assertRedirects(response, redirect_url)
