import logging
import re
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from slackclient import SlackClient
from .models import SlackUser, Badge

logger = logging.getLogger('django')
sc = SlackClient(settings.SLACK_TOKEN)

slash_pointz_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<score_delta>[+-]?\d+))?')
slash_badgz_pattern = re.compile(r'(?P<user><@(?P<user_id>U[A-Z0-9]+)(\|(?P<username>\S+))?>)( (?P<badge>\S+))')


def profile_response(user, username):
    return JsonResponse({
        'response_type': "in_channel",
        "text": f"{username or 'this user'}'s status:",
        "attachments": [
            {
                "title": "Points:",
                "text": f"{user.score} {settings.POINTZ_UNIT}",
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

        post_receipt(request.POST.get('user_id'), user_id, score_delta)

    return profile_response(user, username)


@require_POST
def slash_badgz(request):
    logger.info(request.POST)
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


@require_POST
def slash_rankingz(request, offset=0, limit=5, ephemeral=True):
    logger.info(request.POST)

    fields = []
    users = SlackUser.objects.all().order_by('-score')
    if users.count() > 0:
        padding = len(str(users[0].score))
    else:
        padding = 0

    for rank, user in enumerate(users[offset:offset + limit], start=offset + 1):
        fields.append({
            'value': f'*#{rank}: <@{user.user_id}>*',
        })
        fields.append({
            'value': f'{user.score: >{padding}} {settings.POINTZ_UNIT}'
        })

    actions = []

    if ephemeral:
        if offset >= limit:
            actions.append({
                'name': 'previous',
                'text': ':arrow_left:',
                'type': 'button',
                'value': str(offset - limit),
            })
        actions.append({
            'name': 'post',
            'text': ':arrow_double_down:',
            'type': 'button',
            'value': str(offset),
        })
        if offset + limit < users.count():
            actions.append({
                'name': 'next',
                'text': ':arrow_right:',
                'type': 'button',
                'value': str(offset + limit),
            })

    return JsonResponse({
        'response_type': 'ephemeral' if ephemeral else 'in_channel',
        'replace_original': ephemeral,
        'text': 'Pointz Rankingz',
        'fallback': 'The user rankings !',
        'attachments': [{
            'callback_id': 'rankingz',
            "color": "#6a89cc",
            'fields': fields,
            'actions': actions
        }],
    })


def post_receipt(giver_id, receiver_id, count):
    count = int(count)
    if settings.RECEIPT_CHANNEL and count:

        if count < 0:
            text = f'<@{giver_id}> took away {abs(count)} {settings.POINTZ_UNIT} from <@{receiver_id}>'
        else:
            text = f'<@{giver_id}> gave {abs(count)} {settings.POINTZ_UNIT} to <@{receiver_id}>'

        call = sc.api_call(
            'chat.postMessage',
            channel=settings.RECEIPT_CHANNEL,
            text=text
        )

        logger.info(call)