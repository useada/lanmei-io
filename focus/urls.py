
from django.conf.urls import include, url
from . import views
from . import weibo_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index_more/$', views.index_more, name='index_more'),
    url(r'^topic_more/$', views.topic_more, name='topic_more'),

    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.log_in, name='login'),
    url(r'^logout/$', views.log_out, name='logout'),

    url(r'^weibo_login/$', weibo_views.weibo_login, name='weibo_login'),
    url(r'^weibo_check/$', weibo_views.weibo_check, name='weibo_check'),

    url(r'^helper/$', views.helper, name='helper'),
    url(r'^topic_list/$', views.topic_list, name='topic_list'),
    url(r'^(?P<topic_id>[0-9]+)/$', views.topic_handler, name='topic'),
    url(r'^(?P<topic_id>[0-9]+)/(?P<article_page>[0-9]+)/$', views.topic_handler, name='topic'),
    url(r'^add_article/(?P<topic_id>[0-9]+)/$', views.add_article, name='add_article'),
    url(r'^del_article/(?P<topic_id>[0-9]+)/(?P<article_id>[0-9]+)/$', views.del_article, name='del_article'),
    url(r'^edit_article/(?P<topic_id>[0-9]+)/(?P<article_id>[0-9]+)/$', views.edit_article, name='edit_article'),

    url(r'^add_comment/(?P<topic_id>[0-9]+)/(?P<article_id>[0-9]+)/$', views.add_comment, name='add_comment'),
    url(r'^del_comment/(?P<topic_id>[0-9]+)/(?P<article_id>[0-9]+)/(?P<comment_id>[0-9]+)/$', views.del_comment, name='del_comment'),

    url(r'^comment/(?P<topic_id>[0-9]+)/(?P<article_id>[0-9]+)/(?P<comment_page>[0-9]+)/$', views.comment_handler, name='comment'),


    url(r'^poll/(?P<topic_id>[0-9]+)/(?P<article_id>[0-9]+)/$', views.poll_handler, name='poll_handler'),

    url(r'^people/(?P<people_salt>[0-9a-zA-Z]+)$', views.people_handler, name='people_handler'),
]
