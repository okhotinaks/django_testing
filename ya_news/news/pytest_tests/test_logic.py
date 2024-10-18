"""Этот модуль тестирует логику проекта YaNews."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_for_args, form_data):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=news_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, news_for_args, form_data):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=news_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


def test_user_cant_use_bad_words(author_client, news_for_args, form_data):
    """Пользователь не может использовать недопустимые слова в комментарии."""
    url = reverse('news:detail', args=news_for_args)
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment_data, news_for_args):
    """Автор может редактировать свой комментарий."""
    comment, form_data = comment_data
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(
        response, f'{reverse("news:detail", args=news_for_args)}#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(not_author_client, comment_data):
    """Другие пользователи не могут редактировать чужие комментарии."""
    comment, form_data = comment_data
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']


def test_author_can_delete_comment(author_client, comment, news_for_args):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(
        response, f'{reverse("news:detail", args=news_for_args)}#comments'
    )
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment(not_author_client, comment):
    """Другие пользователи не могут удалять чужие комментарии."""
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
