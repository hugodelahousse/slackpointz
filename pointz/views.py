import logging
import random
import re
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from .models import SlackUser

logger = logging.getLogger('django')
NO_TEXT = ['Gimme some info dawg !']

slash_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<score_delta>[+-]?\d+))?')


def slack_response(text, response_type="in_channel"):
    return JsonResponse({
        'response_type': response_type,
        'text': text
    })


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

    if not user_id:
        return HttpResponse(status=400)

    user, created = SlackUser.objects.get_or_create(user_id=user_id)

    if score_delta:
        if user.user_id == request.POST.get('user_id'):
            return HttpResponse('You can\'t give yourself points, silly !')
        user.increase_score(score_delta)
        return slack_response(f'@{username or "this user"}\'s score is now: {user.score}')
    elif result.group('user_id'):
        return slack_response(f'@{username} has {user.score} points !')
