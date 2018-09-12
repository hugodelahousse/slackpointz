from django.db import models
from django.db.models import F


class SlackUser(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    score = models.IntegerField(default=0)

    def increase_score(self, score_delta):
        SlackUser.objects.filter(user_id=self.user_id).update(score=F('score') + score_delta)
        self.refresh_from_db(fields=['score'])
