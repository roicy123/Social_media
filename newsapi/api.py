import requests

API_KEY = '38cb32e4f8e34c22a328db8ef5a25661'  # Replace with your actual API key
API_URL = 'https://newsapi.org/v2'

def get_top_headlines(country='us'):
    url = f'{API_URL}/top-headlines?country={country}&apiKey={API_KEY}'
    response = requests.get(url)
    return response.json()

def get_everything(q, language='en'):
    url = f'{API_URL}/everything?q={q}&language={language}&apiKey={API_KEY}'
    response = requests.get(url)
    return response.json()