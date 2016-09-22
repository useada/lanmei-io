# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

#################################################
# from django.conf import settings
import urllib
import urllib2
import simplejson as json
# from manager.models import MyUser
from django.contrib.auth import authenticate, login, logout
# from django.http import HttpResponseRedirect


class UserManager(BaseUserManager):
    """通过邮箱，密码创建用户"""
    def create_user(self, email, username, password=None, type=None, **kwargs):
        if not email:
            raise ValueError(u'用户必须要有邮箱')

        user = self.model(
            email=UserManager.normalize_email(email),
            username=username,
            type=type if type else 0
        )
        user.set_password(password)
        if kwargs:
            if kwargs.get('sex', None): user.sex = kwargs['sex']
            # if kwargs.get('is_active', None): user.is_active=kwargs['is_active']
            # if kwargs.get('uid', None): user.uid=kwargs['uid']
            if kwargs.get('salt', None): user.salt = kwargs['salt']
            if kwargs.get('grade', None): user.url = kwargs['grade']
            if kwargs.get('profile', None): user.profile = kwargs['profile']
            if kwargs.get('avatar', None): user.avatar = kwargs['avatar']

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email,
                                password=password,
                                username=username,
                                grade=9,
                                )
        # user.is_admin = True
        user.save(using=self._db)
        return user

    def get_user_by_email(self, email):
        query = self.get_queryset().filter(email=email)
        if query.count() > 0:
            return query[0]
        else:
            return None

    def get_user_by_username(self, username):
        pass


class CustomAuth(object):
    """自定义用户验证"""
    def authenticate(self, email=None, password=None):
        try:
            user = MyUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except MyUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = MyUser.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except MyUser.DoesNotExist:
            return None


###############################################################################
class TopicManager(models.Manager):
    def query_by_column(self, column_id):
        query = self.get_queryset().filter(column_id=column_id)
        return query

    # def query_by_user(self, user_id):
    #     user = User.objects.get(id=user_id)
    #     article_list = user.article_set.all()
    #     return article_list

    def query_by_polls(self):
        query = self.get_queryset().order_by('poll_num')
        return query

    def query_by_time(self):
        query = self.get_queryset().order_by('-pub_date')
        return query

    def query_by_keyword(self, keyword):
        query = self.get_queryset().filter(title__contains=keyword)
        return query


class ArticleManager(models.Manager):
    def query_by_topic(self, topic_id):
        query = self.get_queryset().filter(topic_id=topic_id).order_by('-poll_num')
        return query

    # def query_by_user(self, user_id):
    #     user = User.objects.get(id=user_id)
    #     article_list = user.article_set.all()
    #     return article_list

    def query_by_polls(self):
        query = self.get_queryset().order_by('-poll_num')
        return query

    def query_by_time(self):
        query = self.get_queryset().order_by('-pub_date')
        return query

    def query_by_keyword(self, keyword):
        query = self.get_queryset().filter(title__contains=keyword)
        return query


class StatusManager(models.Manager):
    def get_current(self):
        try:
            status = self.get(name="current")
            return status
        except:
            return None


class StatisticsManager(models.Manager):

    def get_by_user(self, user):
        query = self.get_queryset().filter(user=user)
        if query.exists():
            return query[0]
        else:
            return None

    def get_by_salt(self, salt):
        query = self.get_queryset().filter(salt=salt)
        if query.exists():
            return query[0]
        else:
            return None


# @python_2_unicode_compatible
# class NewUser(AbstractUser):
#     profile = models.CharField('profile', default='', max_length=256)
#
#     def __str__(self):
#         return self.username


@python_2_unicode_compatible
class MyUser(AbstractBaseUser):
    """扩展User"""
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True, db_index=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    # is_active = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    status = models.IntegerField(default=0)             # 状态,　0:正常,　1:无效
    grade = models.IntegerField(default=0)              # 级别,最低为0,最高为9
    type = models.IntegerField(default=0)				# 类型，0本站，1微博登录
    sex = models.IntegerField(default=0)				# sex, 0 female, 1 male
    # uid = models.CharField(max_length=50, null=True)				# weibo uid
    # access_token = models.CharField(max_length=100, null=True)		# weibo access_token
    # url = models.URLField(null=True)							    # 个人站点
    profile = models.CharField(max_length=200, null=True)		    # 个人信息简介
    avatar = models.CharField(max_length=200, null=True)		    # 头像
    date_joined = models.DateTimeField(auto_now=True, null=True)               # 加入时间
    date_operate = models.DateTimeField(auto_now=True, null=True)              # 数据变化时间

    salt = models.CharField(max_length=64, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.grade >= 9

    def __str__(self):
        return self.username

    @property
    def can_password(self):
        return self.type == 0

    class Meta:
        db_table = 'user'


@python_2_unicode_compatible
class Column(models.Model):
    name = models.CharField('column_name', max_length=256)
    intro = models.TextField('introduction', default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'column'
        verbose_name_plural = 'column'
        ordering = ['name']


@python_2_unicode_compatible
class Topic(models.Model):
    column = models.ForeignKey(Column, blank=True, null=True, verbose_name='belong to')
    author = models.ForeignKey('MyUser')
    status = models.IntegerField(default=0)  # 状态,　0:正常,　1:无效
    content = models.CharField(max_length=256)
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)

    # published = models.BooleanField('notDraft', default=True)
    article_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    poll_num = models.IntegerField(default=0)
    keep_num = models.IntegerField(default=0)

    date_operate = models.DateTimeField(auto_now=True, null=True)
    user_operate = models.ForeignKey('MyUser', related_name="topic_operator", null=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topic'

    objects = TopicManager()


@python_2_unicode_compatible
class Article(models.Model):
    topic = models.ForeignKey(Topic, blank=True, null=True, verbose_name='belong to')
    author = models.ForeignKey('MyUser', blank=True)
    status = models.IntegerField(default=0)  # 状态,　0:正常,　1:无效
    content = models.TextField('content')
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)
    # update_time = models.DateTimeField(auto_now=True, null=True)
    # published = models.BooleanField('notDraft', default=True)
    comment_num = models.IntegerField(default=0)
    # 投票
    poll_num = models.IntegerField(default=0)
    # 收藏
    keep_num = models.IntegerField(default=0)

    date_operate = models.DateTimeField(auto_now=True, null=True)
    user_operate = models.ForeignKey('MyUser', related_name="article_operator", null=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'article'
        verbose_name_plural = 'article'

    objects = ArticleManager()


@python_2_unicode_compatible
class Comment(models.Model):
    author = models.ForeignKey('MyUser', null=True)
    refer_to = models.ForeignKey('MyUser', related_name="refer_to", null=True)
    article = models.ForeignKey(Article, null=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)
    poll_num = models.IntegerField(default=0)

    def __str__(self):
        return self.content


class Poll(models.Model):
    user = models.ForeignKey('MyUser', null=True)
    article = models.ForeignKey(Article, null=True)
    comment = models.ForeignKey(Comment, null=True)


@python_2_unicode_compatible
class Status(models.Model):
    name = models.CharField(max_length=36, unique=True, db_index=True)
    curr_topic = models.ForeignKey(Topic, blank=True, null=True, related_name="curr_topic", verbose_name='current topic')
    objects = StatusManager()

    def __str__(self):
        return self.name


# 统计
@python_2_unicode_compatible
class Statistics(models.Model):
    user = models.ForeignKey('MyUser', null=True)
    salt = models.CharField(max_length=64, unique=True, db_index=True)

    article_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    poll_num = models.IntegerField(default=0)
    fans_num = models.IntegerField(default=0)

    objects = StatisticsManager()

    def __str__(self):
        return self.user.username



# 默认图片
DEFAULT_PIC = 'http://images.cnitblog.com/news/66372/201405/271116202595556.jpg'
# 用户信息
USER_INFO_URL = 'https://api.weibo.com/2/users/show.json'
# 发送微博
SEND_WEIBO_URL = 'https://api.weibo.com/2/statuses/upload_url_text.json'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0'
headers = {'User-Agent': user_agent}


class WeiboUser(object):
    def __init__(self, access_token, uid, request=None, **kwargs):
        self.access_token = access_token
        self.uid = uid
        self.request = request
        self.user_cache = None
        self.kwargs = kwargs

    def get_email(self):
        return str(self.uid) + '@weibo.com'

    def create_user(self):
        """创建用户"""
        user_info = self.get_user_info()
        username = user_info.get('screen_name')
        if MyUser.objects.filter(username=username).exists():
            username += '[weibo]'
        u_id = 0
        try:
            new_user = MyUser.objects.create_user(
                    email=self.get_email(),
                    username=username,
                    password=self.uid,
                    type=1,
                    sex=int(user_info.get('sex', 1)),
                    # uid=self.uid,
                    access_token=self.access_token,
                    # url=user_info.get('url', ''),
                    profile=user_info.get('description', ''),
                    avatar=user_info.get('avatar_large'),
            )
            u_id = new_user.id
        except:
            pass
        self.login()    # 登陆
        return u_id

    def get_user_info(self):
        """获取微博用户信息"""
        data = {'access_token': self.access_token, 'uid': self.uid}
        params = urllib.urlencode(data)
        values = urllib2.Request(USER_INFO_URL+'?%s' % params, headers=headers)
        response = urllib2.urlopen(values)
        result = json.loads(response.read())
        if result.get('error_code', None):
            print '获取用户信息失败'
            return False
        return result

    def send_weibo(self):
        """用户发送微博"""
        status = self.kwargs.get('status', None)    # 微博内容
        visible = self.kwargs.get('visible', 0)     # 微博的可见性，0：所有人能看，1：仅自己可见，2：密友可见，3：指定分组可见，默认为0。
        url = self.kwargs.get('url', DEFAULT_PIC)   # 配图
        result = {}
        if status:
            data = {'access_token': self.access_token, 'status': status, 'visible': visible, 'url': url}
            params = urllib.urlencode(data)
            values = urllib2.Request(USER_INFO_URL+'?%s' % params, headers=headers)
            response = urllib2.urlopen(values)
            result = json.loads(response.read())
            if result.get('error_code', None):
                print '发送微博失败'
                return False
            return True
        return result

    def login(self):
        """登陆"""
        email = self.get_email()
        user_ = MyUser.objects.filter(email=email)[0]
        user = authenticate(email=user_.email, password=self.uid)
        login(self.request, user)
