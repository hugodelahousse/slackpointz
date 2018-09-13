from django.db import models
from django.db.models import F
import re


class Badge(models.Model):
    badge = models.CharField(max_length=100, unique=True)

    @staticmethod
    def is_valid_badge(badge_emoji):
        return re.match(r':\S+:', badge_emoji)


class SlackUser(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    score = models.IntegerField(default=0)
    badges = models.ManyToManyField(Badge, related_name='users')

    def increase_score(self, score_delta):
        SlackUser.objects.filter(user_id=self.user_id).update(score=F('score') + score_delta)
        self.refresh_from_db(fields=['score'])

    @property
    def badges_text(self):
        return ''.join([badge.badge for badge in self.badges.all()])

    @property
    def rank(self):
        return SlackUser.objects.filter(score__gt=self.score).count() + 1
