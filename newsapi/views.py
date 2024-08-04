from django.shortcuts import render
from .api import get_top_headlines, get_everything

def top_headlines(request):
    data = get_top_headlines()
    articles = data.get('articles', [])
    for article in articles:
        if 'urlToImage' not in article or not article['urlToImage']:
            article['urlToImage'] = 'https://via.placeholder.com/150'  # Placeholder image URL
    return render(request, 'top_headlines.html', {'articles': articles})

def search(request):
    query = request.GET.get('q')
    if query:
        data = get_everything(q=query)
        articles = data.get('articles', [])
        for article in articles:
            if 'urlToImage' not in article or not article['urlToImage']:
                article['urlToImage'] = 'https://via.placeholder.com/150'  # Placeholder image URL
        return render(request, 'search.html', {'articles': articles})
    else:
        return render(request, 'search.html', {'error': 'Please enter a search query.'})
