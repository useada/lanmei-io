from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Article, Comment, Poll, NewUser
from .forms import CommmentForm, LoginForm, RegisterForm, SetInfoForm, SearchForm, ArticleForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import (
    Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect,
)

import markdown2
import urlparse


def index(request):
    latest_article_list = Article.objects.query_by_time()
    login_form = LoginForm()
    context = {'latest_article_list': latest_article_list, 'login_form': login_form}
    return render(request, 'index.html', context)


def topic_handler(request, topic_id, article_page=1):
    topic = get_object_or_404(Topic, id=topic_id)
    login_form = LoginForm()
    article_form = ArticleForm()
    comment_form = CommmentForm()

    article_set = Article.objects.query_by_topic(topic_id)
    article_paginator = Paginator(article_set, 5)
    try:
        article_list = article_paginator.page(article_page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        article_list = article_paginator.page(1)
        article_page = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        article_list = article_paginator.page(article_paginator.num_pages)
        article_page = article_paginator.num_pages

    for article in article_list:
        article.comment_list, article.comment_page_num, article.comment_page = get_comment(article, 1)

    topic.article_page = article_page
    topic.total_article_page = article_paginator.num_pages

    return render(request, 'topic_page.html', {
        'topic': topic,
        'login_form': login_form,
        'article_form': article_form,
        'article_list': article_list,
        'article_page_num': article_paginator.num_pages,
        'comment_form': comment_form,
    })


def get_comment(article, comment_page):
    comment_set = article.comment_set.get_queryset()
    comment_paginator = Paginator(comment_set, 1)

    try:
        comment_list = comment_paginator.page(comment_page)
        page = comment_page
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        comment_list = comment_paginator.page(1)
        page = 1
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        comment_list = comment_paginator.page(comment_paginator.num_pages)
        page = comment_paginator.num_pages
    return comment_list, comment_paginator.num_pages, page


def comment_handler(request, topic_id, article_id, comment_page):
    topic = get_object_or_404(Topic, id=topic_id)
    article = get_object_or_404(Article, id=article_id)
    comment_form = CommmentForm()
    article.comment_list, article.comment_page_num, article.comment_page = get_comment(article, comment_page)
    return render(request, 'comment.html', {
        'topic': topic,
        'article': article,
        'comment_form': comment_form,
    })



@login_required
def add_article(request, topic_id):
    form = ArticleForm(request.POST)
    url = urlparse.urljoin('/focus/', str(topic_id) + '/9999')
    if form.is_valid():
        user = request.user
        topic = Topic.objects.get(id=topic_id)
        content = form.cleaned_data['content']
        article = Article(topic=topic, author=user, content=content)
        article.save()
    return redirect(url)


@login_required
def edit_article(request, topic_id, article_id):
    form = ArticleForm(request.POST)
    if form.is_valid():
        # user = request.user
        # topic = Topic.objects.get(id=topic_id)
        article = get_object_or_404(Article, id=article_id)
        article.content = form.cleaned_data['content']
        # article = Article(topic=topic, author=user, content=content)
        article.save()
    return HttpResponse("ok");


@login_required
def del_article(request, topic_id, article_id):
    # topic = get_object_or_404(Topic, id=topic_id)
    article = get_object_or_404(Article, id=article_id)

    if article.author_id != request.user.id:
        pass
    else:
        Article.delete(article)
    url = urlparse.urljoin('/focus/', topic_id)
    return redirect(url)


@login_required
def add_comment(request, topic_id, article_id):
    form = CommmentForm(request.POST)
    url = urlparse.urljoin('/focus/comment/', topic_id + '/' + article_id + '/' + str(9999))
    if form.is_valid():
        user = request.user
        # topic = Topic.objects.get(id=topic_id)
        article = Article.objects.get(id=article_id)
        content = form.cleaned_data['content']
        comment = Comment(author=user, content=content, article=article)
        comment.save()
        article.comment_num += 1
        article.save()
    return redirect(url)


@login_required
def del_comment(request, topic_id, article_id, comment_id):
    # topic = get_object_or_404(Topic, id=topic_id)
    article = get_object_or_404(Article, id=article_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author_id != request.user.id:
        pass
    else:
        Comment.delete(comment)
        url = urlparse.urljoin('/focus/comment/', topic_id + '/' + article_id + '/' + str(1))
    article.comment_num -= 1
    article.save()
    return redirect(url)


# submit article for topic
def article_handler(request, topic_id):
    # try:   # since visitor input a url with invalid id
    #     article = Article.objects.get(pk=article_id)  # pk???
    # except Article.DoesNotExist:
    #     raise Http404("Article does not exist")
    topic = get_object_or_404(Topic, id=topic_id)

    article = get_object_or_404(Article, id=article_id)
    content = markdown2.markdown(article.content, extras=["code-friendly",
        "fenced-code-blocks", "header-ids", "toc", "metadata"])
    commentform = CommmentForm()
    loginform = LoginForm()
    comments = article.comment_set.all

    return render(request, 'article_page.html', {
        'article': article,
        'loginform':loginform,
        'commentform':commentform,
        'content': content,
        'comments': comments
        })


@login_required
def get_keep(request, article_id):
    logged_user = request.user
    article = Article.objects.get(id=article_id)
    articles = logged_user.article_set.all()
    if article not in articles:
        article.user.add(logged_user)  # for m2m linking, have tested by shell
        article.keep_num += 1
        article.save()
        return redirect('/focus/')
    else:
        url = urlparse.urljoin('/focus/', article_id)
        return redirect(url)

@login_required
def get_poll_article(request,article_id):
    logged_user = request.user
    article = Article.objects.get(id=article_id)
    polls = logged_user.poll_set.all()
    articles = []
    for poll in polls:
        articles.append(poll.article)

    if article in articles:
        url = urlparse.urljoin('/focus/', article_id)
        return redirect(url)
    else:
        article.poll_num += 1
        article.save()
        poll = Poll(user=logged_user, article=article)
        poll.save()
        data = {}
        return redirect('/focus/')


def log_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['uid']
            password = form.cleaned_data['pwd']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                url = request.POST.get('source_url','/focus')
                return redirect(url)
            else:
                return render(request,'login.html', {'form':form, 'error': "password or username is not ture!"})

        else:
            return render(request, 'login.html', {'form': form})

@login_required
def log_out(request):

    url = request.POST.get('source_url', '/focus/')
    logout(request)
    return redirect(url)

def register(request):
    error1 = "this name is already exist"
    valid = "this name is valid"

    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if request.POST.get('raw_username', 'erjgiqfv240hqp5668ej23foi') != 'erjgiqfv240hqp5668ej23foi':  # if ajax
            try:
                user = NewUser.objects.get(username=request.POST.get('raw_username', ''))
            except ObjectDoesNotExist:
                return render(request, 'register.html', {'form': form, 'msg': valid})
            else:
                return render(request, 'register.html', {'form': form, 'msg': error1})

        else:
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password1 = form.cleaned_data['password1']
                password2 = form.cleaned_data['password2']
                if password1 != password2:
                    return render(request, 'register.html', {'form': form, 'msg': "two password is not equal"})
                else:
                    user = NewUser(username=username, email=email, password=password1)
                    user.save()
                    # return render(request, 'login.html', {'success': "you have successfully registered!"})
                    return redirect('/focus/login')
            else:
                return render(request, 'register.html', {'form': form})


