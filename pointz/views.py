import logging
import random
import re
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import SlackUser

logger = logging.getLogger('django')
NO_TEXT = ['Gimme some info dawg !']

slash_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)\|(?P<username>\S+)>)( (?P<score_delta>[+-]?\d+))?')

@require_POST
def slash_pointz(request):
    logger.debug(request.POST)

    command_text = request.POST.get('text')
    if not command_text:
        return HttpResponse(random.choice(NO_TEXT))

    result = slash_pattern.match(command_text)

    if not result:
        return HttpResponse('Usage: /pointz @username [points]')

    user_id = result.group('user_id')
    username = result.group('username')
    score_delta = result.group('score_delta')

    if not user_id or not username:
        return HttpResponse(status=400)

    user, created = SlackUser.objects.get_or_create(user_id=user_id)

    if score_delta:
        user.increase_score(score_delta)
        return HttpResponse(f'@{username}\'s score is now: {user.score}')
    elif result.group('user_id'):
        return HttpResponse(f'@{username} has {user.score} points !')
