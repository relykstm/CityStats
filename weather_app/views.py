import requests
from django.shortcuts import render, redirect
from django.contrib import messages

def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=6aac762c309ab62e1a9c2663d6aff64a'
    
    if request.method=='POST':
        city = request.POST['city']
    else:
        city = 'Seattle'

    r = requests.get(url.format(city)).json()

    try:
        print(r['main']['temp'])
    except KeyError:
        messages.error(request, "City name not found.")
        return redirect ('/weather')

    city_weather = {
        'city': city,
        'temperature':r['main']['temp'],
        'icon': r['weather'][0]['icon']
    }


    context = {
        'city_weather':city_weather
    }

    return render(request, 'weather_home.html', context)
