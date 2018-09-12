from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger('django')


@require_POST
def slash_pointz(request):
    logger.debug(request.POST)

    return HttpResponse(status=200)
