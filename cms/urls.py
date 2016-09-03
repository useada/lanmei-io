from django.conf.urls import include, url
from django.contrib import admin
from focus import urls as focus_urls
from focus import views
from captcha import urls as captcha_url
from django.conf import settings


urlpatterns = [
    # Examples:
    # url(r'^$', 'cms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^focus/', include(focus_urls)),
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^captcha/', include(captcha_url)),
]

if settings.DEBUG is False:
    urlpatterns.append( url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT, }))
