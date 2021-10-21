from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(
        unique=True,
        max_length=200, verbose_name='Строка для уникального URL-адреса'
    )
    description = models.TextField(verbose_name='Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(
        null=True,
        max_length=400,
        verbose_name='Текст поста',
        help_text='Текст нового поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:20]

    class Meta:
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name='Пост',
        help_text='Пост, к которому будет оставлен комментарий'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        null=True,
        max_length=400,
        verbose_name='Текст комментария',
        help_text='Текст нового комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации комментария'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='follower',
        blank=True,
        null=True,
        verbose_name='Имя подписчика',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='following',
        blank=True,
        null=True,
        verbose_name='Имя автора',
    )
