from .forms import PostCreationForm
from .models import Post
from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class Home(TemplateView):
    
    template_name = 'posts/home.html'

    def get(self, request):
        form = PostCreationForm()
        posts = Post.objects.all()
        args = {'posts': posts, 'form': form}
        return render(request, self.template_name, args)

    def post(self, request):
        form = PostCreationForm(request.POST)
        if form.is_valid():
            saved_post = form.save(commit=False)
            saved_post.user = request.user
            saved_post.save()
            return redirect('posts:home')

        args = {'form': form}
        return render(request, self.template_name, args)