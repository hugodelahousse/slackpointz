"""slackpointz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import json
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.views.decorators.http import require_POST
import logging

from pointz.views import slash_rankingz
from bookz.views import search_book_response

logger = logging.getLogger('django')

@require_POST
def actionz(request):
    logger.info(request.POST)
    payload = json.loads(request.POST.get('payload'))
    action = payload.get('actions')[0]
    logger.info(payload)

    if payload.get('callback_id') == 'rankingz':
        offset = int(action.get('value'))
        if action.get('name') == "post":
            return slash_rankingz(request, offset=offset, ephemeral=False)
        return slash_rankingz(request, offset=offset)
    elif payload.get('callback_id') == 'bookz_subscribe':
        search_string, index = action.get('value').split('|')
        index = int(index)
        return search_book_response(search_string, index)
    else:
        return HttpResponse(status=400)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('actionz/', actionz),
    path('', include('pointz.urls')),
    path('', include('bookz.urls')),
]
