# -*- coding: utf-8 -*-

# from django.shortcuts import render, redirect, get_object_or_404
from .models import MyUser, WeiboUser, Statistics
from cms.settings import APP_KEY, APP_SERCET, CALLBACK_URL
from django.http import (
    Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect,
)
import datetime

from weibo import Client as WeiboClient


def weibo_login(request):
    c = WeiboClient(APP_KEY, APP_SERCET, CALLBACK_URL)
    # print c.authorize_url
    return HttpResponseRedirect(c.authorize_url)


def weibo_check(request):
    code = request.GET.get('code', None)
    # now = datetime.datetime.now()
    if code:
        c = WeiboClient(APP_KEY, APP_SERCET, CALLBACK_URL)
        c.set_code(code)

        show = c.get('users/show', uid=c.uid)
        uid = c.uid
        access_token = c.access_token
        screen_name = show['screen_name']
        description = show['description']
        avatar_large = show['avatar_large']
        gender = show['gender']
        if gender == 'm':
            sex = 1
        else:
            sex = 0

        # request.session['expires_in'] = c.expires_at

        # r = client.request_access_token(code)
        # access_token = r.access_token   # 返回的token，类似abc123xyz456
        # expires_in = r.expires_in       # token过期的UNIX时间：http://zh.wikipedia.org/wiki/UNIX%E6%97%B6%E9%97%B4
        # uid = r.uid
        # 在此可保存access token
        # client.set_access_token(access_token, expires_in)
        # request.session['access_token'] = access_token
        # request.session['expires_in'] = expires_in
        # request.session['uid'] = uid

        weibo_user = WeiboUser(access_token=access_token, uid=uid, screen_name=screen_name, sex=sex,
                         description=description, avatar_large=avatar_large, request=request)      # 实例化超级微博类
        # 更新数据库
        my_user = MyUser.objects.filter(email=weibo_user.get_email())
        if my_user.exists():
            # my_user.update(last_login=now)
            weibo_user.login()
            return HttpResponseRedirect('/')
        else:
            # 创建用户并登陆
            my_user = weibo_user.create_user()
            if my_user is not None:
                stat = Statistics(user=my_user, salt=my_user.salt)
                stat.save()
                weibo_user.login()
                return HttpResponseRedirect('/')
    return HttpResponse('/404/')


