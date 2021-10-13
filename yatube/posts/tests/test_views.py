from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Post text for TEST',
            group=cls.group,
        )
        cls.posts_list = [
            Post.objects.create(
                author=cls.user,
                text='Post text for TEST',
                group=cls.group
            )
            for i in range(15)
        ]
        cache.clear()
        cls.other_group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-other_slug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client(self.user)
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес(view функция) использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('posts:posts_index'): 'posts/index.html',
            reverse('posts:posts_group', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'HasNoName'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_page_show_correct_context(self):
        """Проверяем Context страницы index"""
        response = self.authorized_client.get(reverse('posts:posts_index'))
        for post in response.context['page_obj']:
            self.assertIsInstance(post, Post)

    def test_post_posts_groups_page_show_correct_context(self):
        """Проверяем Context страницы posts_groups"""
        response = self.authorized_client.get(
            reverse('posts:posts_group', kwargs={'slug': 'test-slug'}))
        for post in response.context['page_obj']:
            self.assertEqual(post.group, self.group)

    def test_post_profile_page_show_correct_context(self):
        """Проверяем Context страницы profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        for post in response.context['page_obj']:
            self.assertEqual(post.author, self.user)

    def test_post_post_detail_page_show_correct_context(self):
        """Проверяем Context страницы post_detail"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        post_pk = response.context['post'].pk
        self.assertEqual(post_pk, self.post.pk)

    def test_post_posts_edit_page_show_correct_context(self):
        """Проверяем Context страницы post_edit"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_post_create_page_show_correct_context(self):
        """Проверяем Context страницы post_create"""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_new_create(self):
        """Проверяем, что при создании поста:
        пост появляется на главной странице,
        на странице выбранной группы,
        в профайле пользователя"""
        new_post = Post.objects.create(
            author=self.user,
            text='Post text for TEST',
            group=self.group
        )
        exp_pages = [
            reverse('posts:posts_index'),
            reverse(
                'posts:posts_group', kwargs={'slug': 'test-slug'}),
            reverse(
                'posts:profile', kwargs={'username': 'HasNoName'})
        ]
        for rev in exp_pages:
            with self.subTest(rev=rev):
                response = self.authorized_client.get(rev)
                self.assertIn(
                    new_post, response.context['page_obj']
                )

    def test_post_new_not_in_group(self):
        """Проверяем, что созданный пост не попал в другую группу,
        для которой не был предназначен."""
        new_post = Post.objects.create(
            author=self.user,
            text='Post text for TEST',
            group=self.group
        )
        response = self.authorized_client.get(
            reverse(
                'posts:posts_group',
                kwargs={'slug': 'test-other_slug'})
        )
        self.assertNotIn(new_post, response.context['page_obj'])
