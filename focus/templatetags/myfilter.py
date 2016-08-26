# -*- coding: utf-8 -*-

from django import template

from django.core.urlresolvers import reverse

import datetime

from django.template.defaultfilters import timesince as _timesince
from django.template.defaultfilters import date as _date
from django.utils.timezone import LocalTimezone
from django.utils.translation import ugettext_lazy as _

from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

register = template.Library()


@register.filter
def my_timeslice2(d, now=None):
    # Convert datetime.date to datetime.datetime for comparison.
    if not d:
        return ''
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)
    if not now:
        # if d.tzinfo:
        #     now = datetime.datetime.now(LocalTimezone(d))
        # else:
        now = datetime.datetime.now()
    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since // (60 * 60 * 24) < 3:
        return _("%s 以前") % _timesince(d)
    return _date(d, "Y-m-d H:i")


@register.filter
def my_date(d, now=None):
    if not d:
        return ""
    if not now:
        now = datetime.datetime.now();
    d = d.replace(tzinfo=None)
    delta = now - d
    if delta.seconds < 60:
        return _(u"刚刚")
    elif delta.seconds < 60 * 60:
        return _(u"%s分钟之前") % (delta.seconds/60)
    elif delta.seconds < 60 * 60 * 24:
        return _(u"%s小时之前") % (delta.seconds/60/60)
    else:
        return _date(d, "Y-m-d H:i")
