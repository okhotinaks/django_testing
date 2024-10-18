"""Этот модуль содержит фикстуры для тестирования проекта YaNews."""

import pytest

from django.conf import settings

from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Пользователь - автор."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Пользователь - не автор."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Клиент, авторизованный как Автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент, авторизованный как не автор."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создает новость с заголовком и текстом."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )
    return news


@pytest.fixture
def news_for_args(news):
    """Возвращает ID созданной новости."""
    return (news.id,)


@pytest.fixture
def comment(author, news):
    """Создает комментарий, связанный с новостью, от имени автора."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_for_args(comment):
    """Возвращает ID созданного комментария."""
    return (comment.id,)


@pytest.fixture
def comment_data(author, news):
    """Создает комментарий и возвращает его вместе с обновленными данными."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment, {'text': 'Новый текст'}


@pytest.fixture
def form_data():
    """Возвращает словарь с данными формы для создания комментария."""
    return {'text': 'Новый текст'}


@pytest.fixture
def news_list():
    """Создаёт список новостей."""
    all_news = News.objects.bulk_create(
        News(title=f'Заголовок {i}', text=f'Текст новости {i}')
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    )
    return all_news
