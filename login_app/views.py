from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
import requests
from django_plotly_dash import DjangoDash
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import sqlite3
from django.core import serializers
from django.http import JsonResponse


def index(request):
    return render(request,'index.html')

def register(request):
    errors = user.objects.reg_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags="reg")
        return redirect('/') 
    else:
        new_user = user.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode() )
        request.session['userid'] = new_user.id
    return redirect(f'/homepage')

def logout(request):
    request.session.clear()
    return redirect('/')

def login(request):
    errors = user.objects.login_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags="log")
        return redirect('/')
    else:
        request.session['userid'] = user.objects.get(email=request.POST['email']).id
    return redirect("/homepage")
# ------------------------------------------------------------------------------------------------------------------end login/logout and registration form

def homepage(request):
    if 'userid' not in request.session:
        return redirect('/')
    pollution_url = 'https://api.waqi.info/feed/{}/?token=7d948b48a98a28662fa192ada26908dab5923434'
    
    if request.method=='POST':
        city = request.POST['city']
    else:
        city = 'Seattle'

    pollution_r = requests.get(pollution_url.format(city)).json()
    # print(pollution_r)
    try:
        print(pollution_r['data']['aqi'])
    except:
        messages.error(request, "City name not found.")
        return redirect ('/homepage')

    try:
        print(pollution_r['data']['iaqi']['w']['v'] )
    except:
        messages.error(request, "No wind data for this city")
        return redirect ('/homepage')

    try:
        (pollution_r['data']['iaqi']['co']['v'] )
    except:
        messages.error(request, "No carbon monoxide data for this city")
        return redirect ('/homepage')

    try:
        (pollution_r['data']['iaqi']['p']['v'] )
    except:
        messages.error(request, "No environmental pressure data for this city")
        return redirect ('/homepage')
    
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=6aac762c309ab62e1a9c2663d6aff64a'


    weather_r = requests.get(weather_url.format(city)).json()
    print(weather_r)
    try:
        print(weather_r['main']['temp'])
    except:
        messages.error(request, "City name not found.")
        return redirect ('/homepage')


    aqi = pollution_r['data']['aqi']
    

    if aqi == "-":
        messages.error(request, "City has no data for AQI")
        return redirect ('/homepage')
    
    # this is the checks for the color and impact of the AQI
    if aqi < 50:
        color = '#096'
        impact = "Good"
    elif aqi < 100:
        color = '#ffde33'
        impact = "Moderate"
    elif aqi <150:
        color = '#ff9933'
        impact = "Unhealthy for sensative groups"
    elif aqi < 200:
        color = '#c03'
        impact = "Unhealthy"
    elif aqi < 300:
        color = '#609'
        impact = "Very unhealthy"
    elif aqi < 500:
        color = '#7e0023'
        impact = "Hazardous"

    co = pollution_r['data']['iaqi']['co']['v']
    
    wind = pollution_r['data']['iaqi']['w']['v']
    
    pressure = pollution_r['data']['iaqi']['p']['v']
    

    city_AQI = {
        'city' : city,
        'aqi' : aqi,
        'impact': impact,
        'color' : color,
        'wind': wind,
        'co': co,
        'pressure': pressure
    }

    city_weather = {
        'city': city,
        'temperature':weather_r['main']['temp'],
        'icon': weather_r['weather'][0]['icon']
    }
    
    context = {
        'city_weather':city_weather,
        'city_AQI' : city_AQI
    }
    return render(request, 'homepage.html', context)

def saved_cities(request):
    if 'userid' not in request.session:
        return redirect('/')
    this_user = user.objects.get(id=request.session['userid'])
    these_cities = City.objects.filter(added_by = this_user)
    all_users = user.objects.all()

    context = {
        'cities':these_cities,
        'users': all_users
    }
    return render(request, 'saved_cities.html', context)

def save_new_city(request):
    if 'userid' not in request.session:
        return redirect('/')
    this_user = user.objects.get(id=request.session['userid'])

    City.objects.create(city_name=request.POST['savecity'], temp= int(float(request.POST['temp'])), aqi = int(request.POST['aqi']), added_by=this_user, impact = request.POST['impact'], wind = request.POST['wind'], co = float(request.POST['co']), pressure = float(request.POST['pressure']))

    return redirect('/homepage')

def my_cities_plot(request):
    if 'userid' not in request.session:
        return redirect('/')
    
    this_user = user.objects.get(id=request.session['userid'])

    app = DjangoDash('SimpleExample')   # replaces dash.Dash
    print('IM UPDATING PLOT FROM VIEWS')
    cnx = sqlite3.connect('db.sqlite3')
    
    print(this_user.id)
    
    df = pd.read_sql_query(f"SELECT * FROM login_app_city WHERE added_by_id = {this_user.id}", cnx)
    
    if request.method == 'POST':
        xvalue = request.POST['xaxis']
        yvalue = request.POST['yaxis']
    else:
        xvalue = 'temp'
        yvalue = 'aqi'

    if xvalue == 'temp':
        xtitle = "Temperature"
    if xvalue == 'wind':
        xtitle = "Wind Speed"
    if xvalue == 'pressure':
        xtitle = "Environmental Pressure"
    if xvalue == 'co':
        xtitle = "Carbon Monoxide"
    if xvalue == 'aqi':
        xtitle = "Air Quality Index"

    if yvalue == 'temp':
        ytitle = "Temperature"
    if yvalue == 'wind':
        ytitle = "Wind Speed"
    if yvalue == 'pressure':
        ytitle = "Environmental Pressure"
    if yvalue == 'co':
        ytitle = "Carbon Monoxide"
    if yvalue == 'aqi':
        ytitle = "Air Quality Index"

    xrangelimit = 150
    yrangelimit = 150

    xrangemin = 0
    yrangemin = 0

    if xvalue == 'pressure':
        xrangelimit = 1050
        xrangemin = 1000
    if yvalue == 'pressure':
        yrangelimit = 1050
        yrangemin = 1000

    if xvalue == 'co':
        xrangelimit = 20
    if yvalue == 'co':
        yrangelimit = 20

    if xvalue == 'wind':
        xrangelimit = 20
    if yvalue == 'wind':
        yrangelimit = 20

    if xvalue == 'temp':
        xrangelimit = 120
    if yvalue == 'temp':
        yrangelimit = 120

    cities = City.objects.filter(added_by = this_user)
    
    for city in cities:
        if xvalue == 'aqi':
            if city.aqi > int(xrangelimit):
                xrangelimit = city.aqi + 10
        if yvalue == 'aqi':       
            if city.aqi > int(yrangelimit):
                yrangelimit = city.aqi + 10
        if xvalue == 'temp':
            if city.temp > int(xrangelimit):
                xrangelimit = city.temp + 10
        if yvalue == 'temp':       
            if city.temp > int(yrangelimit):
                yrangelimit = city.temp + 10
        if xvalue == 'wind':
            if city.wind > int(xrangelimit):
                xrangelimit = city.wind + 10
        if yvalue == 'wind':       
            if city.wind > int(yrangelimit):
                yrangelimit = city.wint + 10
        if xvalue == 'co':
            if city.co > int(xrangelimit):
                xrangelimit = city.co + 10
        if yvalue == 'co':       
            if city.co > int(yrangelimit):
                yrangelimit = city.co + 10
        if xvalue == 'pressure':
            if city.pressure > int(xrangelimit):
                xrangelimit = city.pressure + 10
        if yvalue == 'pressure':       
            if city.pressure > int(yrangelimit):
                yrangelimit = city.pressure + 10


    app.layout = html.Div([
        dcc.Graph(
            id='temp-vs-airpollution',
            figure={
                'data': [
                    dict(
                        x=df[df['impact'] == i][xvalue],
                        y=df[df['impact'] == i][yvalue],
                        text=df[df['impact'] == i]['city_name'],
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 15,
                            'line': {'width': 0.5, 'color': 'white'}
                        },
                        name=i
                    ) for i in df.impact.unique()
                ],
                'layout': dict(
                    xaxis={'type': 'scatter', 'title': xtitle, 'range': [xrangemin,xrangelimit]},
                    yaxis={'title': ytitle, 'range': [yrangemin,yrangelimit]},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }
        )
    ])
    context = {
        'user': this_user,
    }

    return render(request, 'my_plot.html', context)

def destroy(request, city_id):
    if 'userid' not in request.session:
        return redirect('/')
    c = City.objects.get(id=city_id)
    c.delete()
    cnx = sqlite3.connect('db.sqlite3')
    df = pd.read_sql_query("SELECT * FROM login_app_city", cnx)
    return redirect('/saved_cities')

def other_user_plot_ajax(request, id):
    this_user = user.objects.get(id=id)
    plot_data = serializers.serialize('json', City.objects.filter(added_by = this_user))
    return JsonResponse(plot_data, safe=False)

