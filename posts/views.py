from .forms import PostCreationForm, CommentForm
from .models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from itertools import chain
from operator import attrgetter

class Home(TemplateView):
    
    template_name = 'posts/home.html'

    def get(self, request):
        form = PostCreationForm()

        following_list = request.user.profile.following.all()
        following_posts_list = Post.objects.filter(user__profile__in=following_list)
        user_posts_list = Post.objects.filter(user=request.user)
        posts_list = sorted(
            chain(following_posts_list, user_posts_list),
            key=attrgetter('date_posted'),
            reverse=True)

        paginator = Paginator(posts_list, 10)
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        most_popular_posts = Post.objects.annotate(
            num_comments=Count('comments')).order_by('-num_comments')[:10]

        args = {
            'posts': posts,
            'most_popular_posts': most_popular_posts,
            'form': form
        }
        return render(request, self.template_name, args)

    def post(self, request):
        form = PostCreationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('posts:home')

        args = {'form': form}
        return render(request, self.template_name, args)


@login_required
def view_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been added.')
            return redirect('posts:view_post', post.slug)
    else:
        form = CommentForm()

    args = {'post': post, 'form': form}
    return render(request, 'posts/view_post.html', args)


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user != post.user:
        raise PermissionDenied()

    if request.method == 'POST':
        form = PostCreationForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been successfully updated.')
            return redirect('posts:view_post', post.slug)
    else:
        form = PostCreationForm(instance=post)

    args = {'post': post, 'form': form}
    return render(request, 'posts/edit_post.html', args)


@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.user != post.user:
        raise PermissionDenied()

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been successfully deleted.')
        return redirect('posts:home')

    args = {'post': post}
    return render(request, 'posts/delete_post_confirm.html', args)
