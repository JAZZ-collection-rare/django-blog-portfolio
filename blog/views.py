from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import RegisterForm, CommentForm
from .models import Category, Post

def home(request):
    posts = Post.objects.filter(status="published").select_related("author", "category")
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query))
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    featured = posts.first()
    page_obj = Paginator(posts, 6).get_page(request.GET.get("page"))
    return render(request, "blog/home.html", {
        "posts": page_obj, "page_obj": page_obj, "featured": featured,
        "categories": Category.objects.all(), "query": query, "selected_category": category_slug,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related("author", "category"), slug=slug, status="published")
    comments = post.comments.filter(is_approved=True).select_related("author")
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post, comment.author = post, request.user
            comment.save()
            messages.success(request, "دیدگاه شما ثبت شد.")
            return redirect(post.get_absolute_url() + "#comments")
    else:
        form = CommentForm()
    return render(request, "blog/detail.html", {"post": post, "comments": comments, "form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, "blog/dashboard.html", {"posts": posts})


@login_required
def create_post(request):
    from .forms import PostForm
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "نوشته ذخیره شد.")
        return redirect("dashboard")
    return render(request, "blog/post_form.html", {"form": form, "heading": "نوشته جدید"})


@login_required
def edit_post(request, pk):
    from .forms import PostForm
    post = get_object_or_404(Post, pk=pk, author=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard")
    return render(request, "blog/post_form.html", {"form": form, "heading": "ویرایش نوشته"})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "نوشته حذف شد.")
        return redirect("dashboard")
    return render(request, "blog/delete_post.html", {"post": post})

