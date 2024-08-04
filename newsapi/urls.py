from django.urls import path
from .views import top_headlines, search

urlpatterns = [
    path('', top_headlines, name='top_headlines'),
    path('search/', search, name='search'),
]