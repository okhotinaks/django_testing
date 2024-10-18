"""Этот модуль тестирует маршруты проекта YaNews."""

from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_for_args')),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Проверка доступности страниц для анонимных пользователей."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_for_args')),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, args, expected_status
):
    """Проверка доступности страниц редактирования и удаления."""
    """для различных пользователей."""
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_for_args')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    """Перенаправление анонимного пользователя на страницу авторизации."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
