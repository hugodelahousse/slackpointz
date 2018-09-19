import random
import requests
from bs4 import BeautifulSoup
from django.db import models
from django.conf import settings
from slackclient import SlackClient

QUOTES_URL = 'https://www.goodreads.com/work/quotes/'
sc = SlackClient(settings.SLACK_TOKEN)


class SlackUser(models.Model):
    user_id = models.CharField(max_length=64, primary_key=True)

    def send_quote(self):
        if not self.subscriptions.count():
            return
        subscription = self.subscriptions.order_by('?').first()
        quote = subscription.get_random_quote()

        sc.api_call('chat.postMessage', channel=self.user_id, attachments=[
            {
                'footer': f"— {quote['author']}",
                'title': quote['book'],
                'text': quote['quote']
            }]
        )

    def __repr__(self):
        return f'<QuotzUser: {self.user_id}>'


class QuotzSubscription(models.Model):
    user = models.ForeignKey(SlackUser, related_name='subscriptions', on_delete=models.CASCADE)
    book_id = models.CharField(max_length=64)

    def __repr__(self):
        return f'<QuotzSubscription: {self.user} subscribed to {self.book_id}>'

    def get_random_quote(self):
        data = requests.get(
            f'{QUOTES_URL}/{self.book_id}',
            params={'format': 'json', 'id': self.book_id, 'page': 1}
        ).json()
        if not data.get('ok'):
            return {'quote': 'There was an error with your quote...', 'author': '', 'book': ''}

        random_page = random.randint(1, data['total_pages'] + 1)

        if random_page != 1:
            data = requests.get(
                f'{QUOTES_URL}/{self.book_id}',
                params={'format': 'json', 'id': self.book_id, 'page': random_page}
            ).json()
            if not data.get('ok'):
                return {'quote': 'There was an error with your quote...', 'author': '', 'book': ''}

        soup = BeautifulSoup(data['content_html'], 'lxml')
        quote = random.choice(list(soup.find_all('article')))


        return {
            'quote': quote.blockquote.text,
            'author': quote.find('span', class_='quoteAuthor').text.strip().strip(','),
            'book': quote.find('span', class_='quoteBook').text.strip()
        }

