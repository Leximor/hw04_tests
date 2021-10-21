import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()
login_create_post = reverse('users:login')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='HasNoName')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Post text for TEST',
            group=cls.group,
        )

        cls.other_post = Post.objects.create(
            author=cls.user,
            text='OTHER Post text for TEST',
            group=cls.group,
        )

        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Comment text for TEST'
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cache.clear()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
            'image': self.uploaded.name,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_object = Post.objects.order_by("-id").first()
        self.assertEqual(form_data['text'], last_object.text)
        self.assertEqual(form_data['group'], last_object.group.pk)
        self.assertEqual(form_data['image'], self.uploaded.name)

    def test_edit_post(self):
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
            'image': self.uploaded.name,

        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(form_data['text'], self.post.text)
        self.assertEqual(form_data['group'], self.group.pk)
        self.assertEqual(form_data['image'], self.uploaded.name)

    def test_create_post_guest_client(self):
        """Попытка создания запись от гостевого пользователя"""
        posts_count = Post.objects.count()

        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_create_url = reverse('posts:post_create')
        post_create_redirect = f'{login_create_post}?next={post_create_url}'
        self.assertRedirects(response, post_create_redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_guest_client(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Иной новый текст поста',
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        post_edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        )
        post_edit_redirect = f'{login_create_post}?next={post_edit_url}'
        self.assertRedirects(response, post_edit_redirect)
        self.assertEqual(self.group.pk, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(self.post.text, form_data['text'])

    def test_create_comment_guest_client(self):
        """Попытка создания комментарий от гостевого пользователя"""
        comment_count = Comment.objects.count()

        form_data = {
            'text': self.comment.text,
            'author': self.comment.author,
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post_create_url = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id})
        comment_create_redirect = f'{login_create_post}?next={post_create_url}'
        self.assertRedirects(response, comment_create_redirect)
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_create_comment(self):
        """Авторизованный пользователь создает комментарий к посту."""
        comment_count = Comment.objects.count()

        form_data = {
            'text': self.comment.text,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        last_object = Comment.objects.order_by("-id").first()
        self.assertEqual(form_data['text'], last_object.text)

    def test_cache_index(self):
        """Проверяем, кэш главной страницы"""
        posts_count = Post.objects.count()
        response = self.authorized_client.get('posts:post_index').content
        Post.objects.create(
            author=self.user,
            text=self.other_post.text,
            group=self.group
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

        self.assertEqual(response, (
            self.authorized_client.get('posts:post_index').content))
        cache.clear()
        self.assertEqual(response, (
            self.authorized_client.get('posts:post_index').content))
