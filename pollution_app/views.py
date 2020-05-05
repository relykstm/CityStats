from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import requests


def pollution(request):
    url = 'https://api.waqi.info/feed/{}/?token=7d948b48a98a28662fa192ada26908dab5923434'
    city = 'Seattle'

    r = requests.get(url.format(city)).json()

    city_AQI = {
        'city' : city,
        'aqi' : r['data']['aqi'],
        'impact': r['status'],
    }
    context = {
        'city_AQI' : city_AQI
    }

    return render(request,'pollution.html', context)