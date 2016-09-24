# -*- coding: utf-8 -*-

from django import forms
from models import MyUser
from django.contrib.auth import authenticate, login, logout
from random import random
from captcha.fields import CaptchaField
# from PIL import Image


class LoginForm(forms.Form):
    email = forms.EmailField()
    pwd = forms.CharField()
    captcha = CaptchaField()


    # email = forms.EmailField(label=u'email', max_length=100, widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': u'邮箱', 'required': '', 'autofocus': ''}
    # ))
    # pwd = forms.CharField(label=u'pwd', widget=forms.PasswordInput(
    #     attrs={'class': 'form-control', 'placeholder': u'密码', 'required': ''}
    #     ))
    # auto_login = forms.BooleanField(label=u'记住密码', required=False,
    #                                 widget=forms.CheckboxInput(attrs={'value': 1}),)

    # def __init__(self, request=None, *args, **kwargs):
    #     self.request = request
    #     self.user_cache = None
    #     self.auth_login = None
    #     super(LoginForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     email = self.cleaned_data.get('email')
    #     password = self.cleaned_data.get('pwd')
    #     auto_login = self.cleaned_data.get('auto_login', None)
    #
    #     if email and password:
    #         if not MyUser.objects.filter(email=email).exists():
    #             raise forms.ValidationError(u'该账号不存在')
    #
    #         self.user_cache = authenticate(email=email, password=password)
    #         if self.user_cache is None:
    #             raise forms.ValidationError(u'邮箱或密码错误！')
    #
    #         elif not self.user_cache.is_active:
    #             raise forms.ValidationError(u'该帐号已被禁用！')
    #
    #     if auto_login:	  # 如果用户勾选了自动登录
    #         self.auto_login = True
    #
    #     return self.cleaned_data
    #
    # def get_user_id(self):
    #     """获取用户id"""
    #     if self.user_cache:
    #         return self.user_cache.id
    #     return None
    #
    # def get_user(self):
    #     """获取用户实例"""
    #     return self.user_cache
    #
    # def get_auto_login(self):
    #     """是否勾选了自动登录"""
    #     return self.auth_login
    #
    # def get_user_is_first(self):
    #     """获取用户是否是第一次登录"""
    #     is_first = False
    #     if self.user_cache and self.user_cache.type == -1:
    #         is_first = True
    #         self.user_cache.type == 0
    #         self.user_cache.save()
    #     return is_first


class RegisterForm(forms.Form):
    email = forms.EmailField(label=u'email', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'Email', 'required': '', 'autofocus': ''}
        ),)
    username = forms.CharField(label=u'username', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'UserName', 'required': '', 'autofocus': ''}
    ),)
    pwd = forms.CharField(label=u'pwd', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'密码', 'required': ''}
        ))
    profile = forms.CharField(label=u'profile', required=False, max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': u'Profile', 'autofocus': ''}
    ), )
    captcha = CaptchaField()
    # pwd2 = forms.CharField(label=u'密码(重复)', widget=forms.PasswordInput(
    #     attrs={'class': 'form-control', 'placeholder': u'重复密码', 'required': ''}
    #     )
    # )

    # def __init__(self, request=None, *args, **kwargs):
    #     self.request = request
    #     self.user = None
    #     super(RegisterForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     data = self.cleaned_data
    #     email = data.get('email')
    #     username = data.get('username')
    #     pwd = data.get('pwd')
    #     # pwd2 = data.get('pwd2')
    #     if MyUser.objects.filter(email=email).exists():
    #         raise forms.ValidationError(u'该邮箱已被注册')
    #     # if pwd != pwd2:
    #     #     raise forms.ValidationError(u'两次输入密码不一致')
    #     if len(pwd) < 6:
    #         raise forms.ValidationError(u'密码不能小于6位')
    #     # 用户注册
    #     # type = -1表示首次
    #     avatar = random.choice(range(35))
    #     avatar = '/site_media/avatar/%s.jpg' % avatar
    #
    #     self.user = MyUser.objects.create_user(email=email, username=username, password=pwd, type=-1, avatar=avatar).id
    #     return data
    #
    # def get_user(self):
    #     """获取用户实例"""
    #     return self.user


class PasswordForm(forms.Form):
    oldpwd = forms.CharField(label=u'原始密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'原始密码', 'required': ''}))
    password1 = forms.CharField(label=u'新密码', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'密码长度在5-12位', 'required': ''}))
    password2 = forms.CharField(label=u'在输入一次', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': u'在输入一次', 'required': ''}))
    captcha = CaptchaField()

    # def __init__(self, user=None, *args, **kwargs):
    #     self.user = user
    #     self.newpwd = None
    #     super(PasswordForm, self).__init__(*args, **kwargs)
    #
    # def clean(self):
    #     cleaned_data = super(PasswordForm, self).clean()
    #     oldpwd = cleaned_data.get("oldpwd")
    #     password1 = cleaned_data.get("password1")
    #     password2 = cleaned_data.get("password2")
    #
    #     if not self.user.check_password(oldpwd):
    #         msg = u"原密码错误。"
    #         self._errors["oldpwd"] = self.error_class([msg])
    #         # raise forms.ValidationError(u'原密码错误')
    #     if password1 and password2:
    #         if password1 != password2:
    #             msg = u"两个密码字段不一致。"
    #             self._errors["password2"] = self.error_class([msg])
    #         if not 4 < len(password1) < 13:
    #             msg = u"密码要在5-12位之间。"
    #             self._errors["password1"] = self.error_class([msg])
    #
    #     return cleaned_data


# class AvatarForm(forms.Form):
#     """
#     ===============================================================================
#     function：	用户修改头像
#     developer:	BeginMan
#     add-time	  2014/6/3
#     ===============================================================================
#     """
#     avatar = forms.ImageField(label=u'图片上传', widget=forms.FileInput(
#         attrs={'class': 'form-control', 'placeholder': u'图片上传', 'required': ''})
#                               )
#
#     def clean(self):
#         cleaned_data = super(AvatarForm, self).clean()
#         image = cleaned_data.get("avatar", None)
#         if image:
#             if image.content_type not in ['image/jpeg', 'image/png']:
#                 raise forms.ValidationError(u'你上传的是图片吗？')
#             else:
#                 img = Image.open(image)
#                 w, h = img.size
#                 max_width = max_height = 1000
#                 if w >= max_width or h >= max_height:
#                     raise forms.ValidationError(u'上传的图片要尺寸要小于或等于%s宽，%s高' % (max_width, max_height))
#                 if img.format.lower() not in ['jpeg', 'pjpeg', 'png', 'jpg']:
#                     raise forms.ValidationError(u'暂时只接纳JPEG or PNG.')
#                 #validate file size
#                 if len(image) > (1 * 1024 * 1024):
#                     raise forms.ValidationError('Image file too large ( maximum 1mb )')
#         else:
#             raise forms.ValidationError(u'额，图片呢？')
#         return cleaned_data

# class LoginForm(forms.Form):
#     uid = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' ,'id':'uid', 'placeholder': 'Username'}))
#     pwd = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control' ,'id':'pwd', 'placeholder': 'Password'}))
#
#
# class RegisterForm(forms.Form):
#     username = forms.CharField(label='username', max_length=100,
#         widget=forms.TextInput(attrs={'id':'username', 'onblur': 'authentication()'}))
#     email = forms.EmailField()
#     password1 = forms.CharField(widget=forms.PasswordInput)
#     # password2 = forms.CharField(widget=forms.PasswordInput)


###############################################################################


class SetInfoForm(forms.Form):
    username = forms.CharField()


class ArticleCaptchaForm(forms.Form):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={"id":"editor", "placeholder": u"写下你的文字", "autofocus":"autofocus"}))
    captcha = CaptchaField()


class ArticleForm(forms.Form):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={"id":"editor", "placeholder": u"写下你的文字", "autofocus":"autofocus"}))


class ArticleEditForm(forms.Form):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={"id":"editor", "placeholder": u"写下你的文字", "autofocus":"autofocus"}))


class CommmentForm(forms.Form):
    content = forms.CharField(label='')
    rt = forms.CharField(label='')  # 回复XX


class SearchForm(forms.Form):
    keyword = forms.CharField(widget=forms.TextInput)
