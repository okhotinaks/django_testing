"""Этот модуль тестирует логику проекта YaNews."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import FORM_DATA


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, urls, news_for_args):
    """Анонимный пользователь не может создать комментарий."""
    initial_comment_count = Comment.objects.count()
    response = client.post(urls['detail'](news_for_args), data=FORM_DATA)
    expected_url = urls['expected_redirect'](urls['detail'](news_for_args))
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comment_count


def test_user_can_create_comment(author_client, author, urls, news_for_args):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(
        urls['detail'](news_for_args), data=FORM_DATA
    )
    assertRedirects(response, urls['comments'](news_for_args))
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.news.id == news_for_args[0]
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, urls, news_for_args):
    """Пользователь не может использовать недопустимые слова в комментарии."""
    form_data = FORM_DATA.copy()
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    response = author_client.post(
        urls['detail'](news_for_args), data=form_data
    )
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, urls, comment, comment_for_args, news_for_args):
    """Автор может редактировать свой комментарий."""
    response = author_client.post(
        urls['edit'](comment_for_args), data=FORM_DATA
    )
    assertRedirects(response, urls['comments'](news_for_args))
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']


def test_other_user_cant_edit_comment(
        not_author_client, comment, comment_for_args, urls):
    """Другие пользователи не могут редактировать чужие комментарии."""
    original_values = (comment.text, comment.author, comment.news)
    response = not_author_client.post(
        urls['edit'](comment_for_args), data=FORM_DATA
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert (comment.text, comment.author, comment.news) == original_values


def test_author_can_delete_comment(
        author_client, urls, comment_for_args, news_for_args):
    """Автор может удалить свой комментарий."""
    response = author_client.post(urls['delete'](comment_for_args))
    assertRedirects(response, urls['comments'](news_for_args))
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment(not_author_client, urls, comment_for_args):
    """Другие пользователи не могут удалять чужие комментарии."""
    response = not_author_client.post(urls['delete'](comment_for_args))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
