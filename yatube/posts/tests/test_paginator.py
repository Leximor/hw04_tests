from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.posts = [
            Post.objects.create(
                author=cls.user,
                text='Post text № {i}',
                group=cls.group
            )
            for i in range(15)
        ]
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Паджинатор выводит по 10 записей на страницу."""
        reverse_dict_for_paginator_test = [
            reverse('posts:posts_index'),
            reverse('posts:posts_group', kwargs={
                    'slug': self.group.slug}),
            reverse('posts:profile', kwargs={
                    'username': self.user.username})
        ]
        for reverse_name in reverse_dict_for_paginator_test:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Паджинатор выводит оставшиеся 5 записей на вторую страницу."""
        reverse_dict_for_paginator_test = [
            reverse('posts:posts_index') + '?page=2',
            reverse(
                'posts:posts_group', kwargs={
                    'slug': self.group.slug}) + '?page=2',
            reverse(
                'posts:profile', kwargs={
                    'username': self.user.username}) + '?page=2'
        ]
        for reverse_name in reverse_dict_for_paginator_test:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 5)
