
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_one_page(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_one_page(request, Post.objects.all())
    }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_one_page(request, posts)
    return render(
        request,
        'posts/group_list.html',
        {'page_obj': page_obj, 'group': group}
    )


def profile(request, username):
    author = User.objects.get(username=username)
    posts = author.posts.all()
    page_obj = get_one_page(request, posts)
    following = (request.user.is_authenticated
                 and Follow.objects.filter(
                     user=request.user,
                     author=author).exists()
                 )
    return render(
        request,
        'posts/profile.html',
        {'page_obj': page_obj, 'author': author, 'following': following, }
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = post.comments.all()
    form = CommentForm(request.POST or None)
    author = post.author
    context = {
        'post': post,
        'comment': comment,
        'form': form,
        'author': author,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', username=request.user.username)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    context = {'posts': posts}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(
            user=user,
            author=author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username).delete()
    return redirect('posts:profile', username=username)
