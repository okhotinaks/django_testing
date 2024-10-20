from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()

LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')


def edit_url(slug):
    return reverse('notes:edit', args=(slug,))


class TestListNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Охотина Ксения')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                text='Текст заметки',
                slug=f'test-note_{index}',
                author=cls.author)
            for index in range(10)
        )
        cls.note = Note.objects.first()

    def test_notes_list_for_different_users(self):
        users = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users:
            self.client.force_login(user)
            response = self.client.get(LIST_URL)
            object_list = response.context['object_list']
            self.assertEqual(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        urls = (
            (ADD_URL,),
            (edit_url(self.note.slug),),
        )
        for url in urls:
            with self.subTest(url):
                response = self.author_client.get(url[0])
                self.assertIsInstance(response.context['form'], NoteForm)
