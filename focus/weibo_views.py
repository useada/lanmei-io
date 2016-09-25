# -*- coding: utf-8 -*-

# from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic, Article, Comment, Poll, MyUser, Status, Statistics, WeiboUser
# from .forms import CommmentForm, LoginForm, RegisterForm, SetInfoForm, SearchForm, ArticleForm, ArticleEditForm
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth import authenticate, login, logout
# from django.http import JsonResponse
# from django.views.decorators.cache import cache_page
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cms.settings import APP_KEY, APP_SERCET, CALLBACK_URL

from django.http import (
    Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect,
)

import cms.settings
import datetime

from weibo import Client as WeiboClient


def weibo_login(request):
    c = WeiboClient(APP_KEY, APP_SERCET, CALLBACK_URL)
    print c.authorize_url
    return HttpResponseRedirect(c.authorize_url)


def weibo_check(request):
    code = request.GET.get('code', None)
    now = datetime.datetime.now()
    if code:
        c = WeiboClient(APP_KEY, APP_SERCET, CALLBACK_URL)
        c.set_code(code)

        c.get('users/show', uid=c.uid)
        uid = c.uid
        access_token = c.access_token

        # r = client.request_access_token(code)
        # access_token = r.access_token   # 返回的token，类似abc123xyz456
        # expires_in = r.expires_in       # token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
        # uid = r.uid
        # 在此可保存access token
        # client.set_access_token(access_token, expires_in)
        # request.session['access_token'] = access_token
        # request.session['expires_in'] = expires_in
        # request.session['uid'] = uid

        user = WeiboUser(access_token=access_token, uid=uid, request=request)      # 实例化超级微博类
        # 更新数据库
        my_user = MyUser.objects.filter(email=user.get_email())
        if my_user.exists():
            # my_user.update(last_login=now)
            user.login()    # 登陆
            return HttpResponseRedirect('/')
        else:
            # 创建用户并登陆
            u_id = user.create_user()
            if u_id:
                return HttpResponseRedirect('/')
    return HttpResponse('/404/')


