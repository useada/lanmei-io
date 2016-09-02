from django.contrib import admin
from django.db import models
from django import forms
from .models import Comment, Article, Column, MyUser, Topic, Status, Statistics


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author_id','article_id','pub_date', 'content','poll_num')


class ArticleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
                           attrs={'rows': 41,
                                  'cols': 100
                                  })}, 
    }
    list_display = ('content', 'pub_date', 'poll_num', 'date_operate', 'user_operate')


# class NewUserAdmin(admin.ModelAdmin):
#     list_display = ('username','date_joined', 'profile')


class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'profile')


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('name', 'intro')


class TopicAdmin(admin.ModelAdmin):
    list_display = ('author', 'pub_date', 'poll_num')


class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'curr_topic')


class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'salt')


admin.site.register(Comment, CommentAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Statistics, StatisticsAdmin)
