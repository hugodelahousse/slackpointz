import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('django')

GOODREADS_SEARCH_URL = 'https://www.goodreads.com/search/index.xml'


def search_book_response(search_text, results_index=0):
    if not search_text:
        return HttpResponse('Usage: /quotz_subscribe <Book name>')

    r = requests.get(GOODREADS_SEARCH_URL, params={
        'key': settings.GOODREADS_KEY,
        'q': search_text,
    })
    soup = BeautifulSoup(r.text, 'lxml')

    results = soup.search.results.find_all('work')
    if not results or results_index >= len(results):
        return HttpResponse('No book found...')

    book = results[results_index]

    actions = [{
        'name': 'next',
        'text': 'Search Again',
        'type': 'button',
        'value': f'{search_text}|{results_index + 1 if results_index < len(results) else 0}'
    }, {
        'name': 'subscribe',
        'text': 'Subscribe',
        'style': 'primary',
        'type': 'button',
        'value': book.id.text,
    }]

    response = {
        'text': 'Bookz Picker',
        'attachments': [
            {
                'title': book.title.text,
                'author_name': book.author.find('name').text,
                'image_url': book.image_url.text,
                'thumb_url': book.small_image_url.text,
                'fallback': 'Find a book to subscribe to',
                'callback_id': 'quotz_subscribe',
                'actions': actions
            },
        ]
    }

    return JsonResponse(response)


@require_POST
def slack_quotzsubscribe(request):
    return search_book_response(request.POST.get('text'))

