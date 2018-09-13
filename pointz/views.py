import logging
import re
import grapheme
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from .models import SlackUser, Badge

logger = logging.getLogger('django')

slash_pointz_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<score_delta>[+-]?\d+))?')
slash_badgz_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<badge>\S+))')


def slack_response(text, response_type="in_channel"):
    return JsonResponse({
        'response_type': response_type,
        'text': text
    })


@require_POST
def slash_pointz(request):
    logger.debug(request.POST)

    command_text = request.POST.get('text')
    result = slash_pointz_pattern.match(command_text)

    if not result:
        return HttpResponse('Usage: /pointz @username [points]')

    user_id = result.group('user_id')
    username = result.group('username')
    score_delta = result.group('score_delta')

    if not user_id:
        return HttpResponse(status=400)

    user, _ = SlackUser.objects.get_or_create(user_id=user_id)

    if score_delta:
        if user.user_id == request.POST.get('user_id'):
            return HttpResponse('You can\'t give yourself points, silly !')
        user.increase_score(score_delta)
        return slack_response(f'@{username or "this user"}\'s score is now: {user.score}')
    elif result.group('user_id'):
        return slack_response(f'@{username or "this user"} has {user.score} points !')


@require_POST
def slash_badgz(request):
    logger.debug(request.POST)
    command_text = request.POST.get('text')
    result = slash_badgz_pattern.match(command_text)

    if not result:
        return HttpResponse('Usage: /badgz @username <badge>')

    user_id = result.group('user_id')
    username = result.group('username')
    badge_emoji = result.group('badge')

    if grapheme.length(badge_emoji) != 1 or (len(badge_emoji) == 1 and ord(badge_emoji) < 128):
        return HttpResponse(f'Invalid badge: {badge_emoji}.\nIf you think this is a mistake,'
                            f'feel free to post an issue here: http://github.com/hugodelahousse/slackpointz/issues')
    # Check valid badge

    if user_id == request.POST.get('user_id'):
        return HttpResponse('You can\'t give yourself a badge, silly !')

    user, _ = SlackUser.objects.get_or_create(user_id=user_id)
    badge, _ = Badge.objects.get_or_create(badge=badge_emoji)

    user.badges.add(badge)
    return slack_response(f'@{username or "this user"} has these badges: '
                          f'{"".join([badge.badge for badge in user.badges.all()])}')
