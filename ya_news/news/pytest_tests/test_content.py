"""Этот модуль тестирует контент проекта YaNews."""

import pytest

from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, news_list):
    """Количество новостей на главной странице."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    news_list_count = len(news_list)
    assert news_count == news_list_count


@pytest.mark.django_db
def test_news_order(client):
    """Сортировка новостей."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, news_for_args):
    """Сортировка комментариев."""
    detail_url = reverse('news:detail', args=news_for_args)
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert sorted_timestamps == all_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_for_args):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    detail_url = reverse('news:detail', args=news_for_args)
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_for_args):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    detail_url = reverse('news:detail', args=news_for_args)
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
