"""Этот модуль тестирует маршруты проекта YaNews."""

from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, expected_status',
    (
        ('news:home', None, HTTPStatus.OK),
        ('users:login', None, HTTPStatus.OK),
        ('users:logout', None, HTTPStatus.OK),
        ('users:signup', None, HTTPStatus.OK),
        ('news:detail', pytest.lazy_fixture('news_for_args'), HTTPStatus.OK),
        ('news:edit',
            pytest.lazy_fixture('comment_for_args'), HTTPStatus.FOUND),
        ('news:delete',
            pytest.lazy_fixture('comment_for_args'), HTTPStatus.FOUND),
    )
)
def test_pages_availability(client, name, args, expected_status):
    """Проверка доступности страниц и кодов ответа."""
    url = reverse(name, args=args)
    response = client.get(url)
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
