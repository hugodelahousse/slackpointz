from django.urls import path
from .views import slack_quotzsubscribe

urlpatterns = [
    path('quotz-subscribe/', slack_quotzsubscribe),
]
