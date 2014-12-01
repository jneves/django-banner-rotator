#-*- coding:utf-8 -*-

from random import random

from django.db import models


def pick(bias_list):
    """ Takes a list of 2-tuples [(item, weight)] using weight as the
        probability when calculating an item to choose
    """
    try:
        # First, normalize weights to ensure we
        # have a valid probability distribution
        assert sum([w for i, w in bias_list]) == 1
    except AssertionError:
        norm_const = float(sum([w for i, w in bias_list]))
        distribution = [(i, w / norm_const) for i, w in bias_list]
    else:
        distribution = bias_list

    number = random()
    current = 0.0

    # @link http://fr.w3support.net/index.php?db=so&id=479236
    for choice, probability in distribution:
        current += probability
        if number <= current:
            return choice


class BannerManager(models.Manager):

    def biased_choice(self, place, search=''):
        queryset = self.filter(is_active=True, places=place)

        if not queryset.count():
            raise self.model.DoesNotExist

        search_words = map(lambda s: s.strip().lower(), search.split(','))

        normalizer = 0
        for banner in queryset:
            normalizer += banner.words_weight(search_words)
        return pick([(i, i.weight / float(normalizer)) for i in queryset])
