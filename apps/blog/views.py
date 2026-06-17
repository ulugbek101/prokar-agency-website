from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    posts = Post.objects.filter(is_active=True).prefetch_related('tags')
    tag_filter = request.GET.get('tag')
    if tag_filter:
        posts = posts.filter(tags__name=tag_filter)
    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'tag_filter': tag_filter,
    })


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.filter(is_active=True).prefetch_related('tags'),
        Q(slug_ru=slug) | Q(slug_uz=slug),
    )
    return render(request, 'blog/post_detail.html', {'post': post})
