"""Этот модуль тестирует контент проекта YaNews."""

import pytest

from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, urls, news_list):
    """Количество новостей на главной странице."""
    response = client.get(urls['home'])
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, urls):
    """Сортировка новостей."""
    response = client.get(urls['home'])
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, urls, news_for_args):
    """Сортировка комментариев."""
    response = client.get(urls['detail'](news_for_args))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert sorted_timestamps == all_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, urls, news_for_args):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    response = client.get(urls['detail'](news_for_args))
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, urls, news_for_args):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    response = author_client.get(urls['detail'](news_for_args))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
