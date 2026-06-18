from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    posts = Post.objects.filter(is_active=True).prefetch_related('tags')
    tag_filter = request.GET.get('tag', '').strip()
    query = request.GET.get('q', '').strip()

    if tag_filter:
        posts = posts.filter(tags__name=tag_filter)

    if query:
        posts = posts.filter(
            Q(title_ru__icontains=query) |
            Q(title_uz__icontains=query) |
            Q(body_ru__icontains=query)  |
            Q(body_uz__icontains=query)  |
            Q(tags__name__icontains=query)
        ).distinct()

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'tag_filter': tag_filter,
        'query': query,
    })


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.filter(is_active=True).prefetch_related('tags'),
        Q(slug_ru=slug) | Q(slug_uz=slug),
    )
    return render(request, 'blog/post_detail.html', {'post': post})
