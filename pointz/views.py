import logging
import re
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from .models import SlackUser, Badge

logger = logging.getLogger('django')

slash_pointz_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<score_delta>[+-]?\d+))?')
slash_badgz_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<badge>\S+))')


def profile_response(user, username):
    return JsonResponse({
        'response_type': "in_channel",
        "text": f"{username or 'this user'}'s status:",
        "attachments": [
            {
                "title": "Points:",
                "text": f"{user.score} points",
                "color": "#6a89cc",
                "footer": f"Ranked #{user.rank}"
            },
            {
                "title": "Badges:",
                "text": user.badges_text,
                "color": "#f8c291"
            }
        ]
    })

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

    return profile_response(user, username)


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

    if not Badge.is_valid_badge(badge_emoji):
        return HttpResponse(f'Invalid badge: {badge_emoji}.\nIf you think this is a mistake, '
                            f'feel free to post an issue here: http://github.com/hugodelahousse/slackpointz/issues')
    # Check valid badge

    if user_id == request.POST.get('user_id'):
        return HttpResponse('You can\'t give yourself a badge, silly !')

    user, _ = SlackUser.objects.get_or_create(user_id=user_id)
    badge, _ = Badge.objects.get_or_create(badge=badge_emoji)

    user.badges.add(badge)
    return profile_response(user, username)
