from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import test_view, test_view_hello, test_query

urlpatterns = [
    path('', test_view),
    path('query', csrf_exempt(test_query)),
    path('test-view-hello', test_view_hello),
]
