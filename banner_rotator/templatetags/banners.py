#-*- coding:utf-8 -*-

import logging
import re

from django import template
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from banner_rotator.models import Banner, Place


logger = logging.getLogger('banner_rotator')

register = template.Library()


class BannerNode(template.Node):
    def __init__(self, place_slug, varname=None):
        self.varname, self.place_slug = varname, place_slug

    def render(self, context):
        try:
            self.place = Place.objects.get(slug=self.place_slug)
        except Place.DoesNotExist:
            return ''

        try:
            banner_obj = Banner.objects.biased_choice(self.place)
            banner_obj.view()
        except Banner.DoesNotExist:
            banner_obj = None

        if self.varname:
            context.update({
                self.varname: banner_obj,
                '%s_place' % self.varname: self.place
            })
            return ''
        else:
            templates = [
                #'banner_rotator/place_%s.html' % place.slug,
                'banner_rotator/place.html'
            ]
            return render_to_string(templates, {
                'banner': banner_obj,
                'banner_place': self.place
            })


@register.tag(takes_context=True)
def banner(context, parser, token):
    """
    Use: {% banner place-slug as banner %} or {% banner place-slug %}
    """
    request = context['request']
    bits = token.contents.split()

    if len(bits) not in [2, 4]:
        raise template.TemplateSyntaxError(_("banner tag takes three of four arguments"))

    if 4 == len(bits) and 'as' == bits[2]:
        place_slug = bits[1]
        varname = bits[3]
    else:
        place_slug = bits[1]
        varname = None

    words = map(lambda s: s.lower().strip(), re.split('\W+', request.META['QUERY_STRING']))

    return BannerNode(place_slug, varname, query=words)
