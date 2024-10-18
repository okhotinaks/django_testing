from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListNotes(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Охотина Ксения')
        cls.reader = User.objects.create(username='Читатель')

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
            response = self.client.get(self.LIST_URL)
            object_list = response.context['object_list']
            self.assertEqual(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context['form'], NoteForm)
