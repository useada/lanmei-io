# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Article, Comment, Poll, MyUser, Status, Statistics
from .forms import CommmentForm, LoginForm, RegisterForm, SetInfoForm, SearchForm, ArticleForm, ArticleEditForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from cms.settings import ARTICLE_NUM_ONE_PAGE, COMMENT_NUM_ONE_PAGE

from django.http import (
    Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect,
)

# import markdown2
import urlparse
import os
import json


def index(request):
    status = Status.objects.get_current()
    top10_article_list = Article.objects.query_hot()[:10]
    top10_topic_list = Topic.objects.query_by_time()[:10] #最新
    login_form = LoginForm()
    context = { 'status': status, 'top10_article_list': top10_article_list,
                'top10_topic_list': top10_topic_list,
                'login_form': login_form}
    return render(request, 'index.html', context)


def index_more(request):
    article_index = request.GET.get('article_index', None)
    begin = int(article_index)
    count = begin + 5
    top_article_list = Article.objects.query_hot()[begin:count]
    n = top_article_list.count()
    if n > 0:
        context = {'top_article_list': top_article_list}
        html = render(request, 'index_more.html', context)
        response_data = {'article_index': begin+n, 'content': html.content}
    else:
        response_data = {'article_index': begin, 'content': ''}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def topic_list(request):
    hot_topic_list = Topic.objects.query_by_time()[:10]
    top10_topic_list = Topic.objects.query_by_polls()[:10]
    context = {'topic_list': hot_topic_list,
               'top10_topic_list': top10_topic_list}
    return render(request, 'topic_list.html', context)


def topic_more(request):
    topic_index = request.GET.get('topic_index', None)
    begin = int(topic_index)
    count = begin + 5
    hot_topic_list = Topic.objects.query_by_polls()[begin:count]
    n = hot_topic_list.count()
    if n > 0:
        context = {'topic_list': hot_topic_list}
        html = render(request, 'topic_more.html', context)
        response_data = {'topic_index': begin+n, 'content': html.content}
    else:
        response_data = {'topic_index': begin, 'content': ''}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def helper(request):
    return render(request, 'helper.html', {})


def topic_handler(request, topic_id, article_page=1):
    topic = get_object_or_404(Topic, id=topic_id)
    login_form = LoginForm()
    article_form = ArticleForm()
    comment_form = CommmentForm()

    article_set = Article.objects.query_by_topic(topic_id)
    article_paginator = Paginator(article_set, ARTICLE_NUM_ONE_PAGE)
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

    # article_list.count()

    return render(request, 'topic_page.html', {
        'topic': topic,
        'title': topic.content,
        'login_form': login_form,
        'article_form': article_form,
        'article_list': article_list,
        'article_page_num': article_paginator.num_pages,
        'comment_form': comment_form,
    })


def get_comment(article, comment_page):
    comment_set = article.comment_set.get_queryset()
    comment_paginator = Paginator(comment_set, COMMENT_NUM_ONE_PAGE)

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
        topic.article_num += 1
        topic.save()

        stat = Statistics.objects.get_by_user(user)
        if stat is not None:
            stat.article_num += 1
            stat.save()
    return redirect(url)


@login_required
def edit_article(request, topic_id, article_id):
    form = ArticleEditForm(request.POST)
    if form.is_valid():
        # user = request.user
        # topic = Topic.objects.get(id=topic_id)
        article = get_object_or_404(Article, id=article_id)
        article.content = form.cleaned_data['content']
        # article = Article(topic=topic, author=user, content=content)
        article.save()
    return HttpResponse("ok")


@login_required
def del_article(request, topic_id, article_id):
    topic = get_object_or_404(Topic, id=topic_id)
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    if article.author_id != request.user.id:
        pass
    else:
        Article.delete(article)
        topic.article_num -= 1
        topic.save()
        stat = Statistics.objects.get_by_user(user)
        if stat is not None:
            stat.article_num -= 1
            stat.save()
    # url = urlparse.urljoin('/focus/', topic_id)
    # return redirect(url)
    return HttpResponse("ok")


@login_required
def add_comment(request, topic_id, article_id):
    form = CommmentForm(request.POST)
    url = urlparse.urljoin('/focus/comment/', topic_id + '/' + article_id + '/' + str(9999))
    if form.is_valid():
        user = request.user
        # topic = Topic.objects.get(id=topic_id)
        article = Article.objects.get(id=article_id)
        content = form.cleaned_data['content']
        rt = form.cleaned_data['rt']
        refer_to = None
        if rt != '0':
            refer_to = MyUser.objects.get(salt=rt)

        comment = Comment(author=user, content=content, refer_to=refer_to, article=article)
        comment.save()
        article.comment_num += 1
        article.save()
        stat = Statistics.objects.get_by_user(user)
        if stat is not None:
            stat.comment_num += 1
            stat.save()

    return redirect(url)


@login_required
def del_comment(request, topic_id, article_id, comment_id):
    # topic = get_object_or_404(Topic, id=topic_id)
    article = get_object_or_404(Article, id=article_id)
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    if comment.author_id != request.user.id:
        pass
    else:
        Comment.delete(comment)
        url = urlparse.urljoin('/focus/comment/', topic_id + '/' + article_id + '/' + str(1))
    article.comment_num -= 1
    article.save()
    stat = Statistics.objects.get_by_user(user)
    if stat is not None:
        stat.comment_num -= 1
        stat.save()
    return redirect(url)


@login_required
def poll_handler(request, topic_id, article_id):
    article = get_object_or_404(Article, id=article_id)
    logged_user = request.user
    polls = logged_user.poll_set.all()
    articles = []
    for poll in polls:
        articles.append(poll.article)

    if article in articles:
        return HttpResponse(str(article.poll_num))
    else:
        article.poll_num += 1
        article.save()
        poll = Poll(user=logged_user, article=article)
        poll.save()

        stat = Statistics.objects.get_by_user(article.author)
        if stat is not None:
            stat.poll_num += 1
            stat.save()
        return HttpResponse(str(article.poll_num))


# @login_required
# def get_keep(request, article_id):
#     logged_user = request.user
#     article = Article.objects.get(id=article_id)
#     articles = logged_user.article_set.all()
#     if article not in articles:
#         article.user.add(logged_user)  # for m2m linking, have tested by shell
#         article.keep_num += 1
#         article.save()
#         return redirect('/focus/')
#     else:
#         url = urlparse.urljoin('/focus/', article_id)
#         return redirect(url)


def log_in(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    if request.method == 'POST':
        msg = "error"
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['pwd']
            user = authenticate(email=email, password=pwd)
            if user is not None:
                login(request, user)
                url = request.POST.get('source_url','/focus')
                return redirect(url)
            else:
                msg = "mismatch"
                return render(request,'login.html', {'form': form, 'msg': msg})
        else:
            return render(request, 'login.html', {'form': form, 'msg': msg})


@login_required
def log_out(request):

    url = request.POST.get('source_url', '/focus/')
    logout(request)
    return redirect(url)


def register(request):
    error = "username exist"
    valid = "username invalid"

    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        raw_username = request.POST.get('raw_username', 'erjgiqfv240hqp5668ej23foi')
        if raw_username != 'erjgiqfv240hqp5668ej23foi':  # if ajax
            try:
                user = MyUser.objects.get(username=raw_username)
            except ObjectDoesNotExist:
                return render(request, 'register.html', {'form': form, 'msg': valid})
            else:
                return render(request, 'register.html', {'form': form, 'msg': error})

        else:
            msg = "error"
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                profile = form.cleaned_data['profile']
                password = form.cleaned_data['pwd']
                try:
                    if MyUser.objects.filter(username=username).exists():
                        msg = "username exist"
                    elif MyUser.objects.filter(email=email).exists():
                        msg = "email exist"
                    else:
                        user = MyUser.objects.create_user(email, username, password, None, profile=profile)
                        salt = user.salt
                        stat = Statistics(user=user, salt=salt)
                        stat.save()
                        msg = "success"
                except:
                    pass
                # return redirect('/focus/login')
                return render(request, 'register.html', {'form': form, 'msg': msg})
            else:
                return render(request, 'register.html', {'form': form, 'msg': msg})


def people_handler(request, people_salt):
    stat = get_object_or_404(Statistics, salt=people_salt)
    return render(request, 'people.html', {"stat": stat})

