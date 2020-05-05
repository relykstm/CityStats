
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('homepage', views.homepage),
    path('saved_cities', views.saved_cities),
    path('save', views.save_new_city),
    path('mycitiesplot', views.my_cities_plot),
    path('logout', views.logout),
    path('destroy/<int:city_id>', views.destroy),
    path('ajax/otheruserplot/<id>', views.other_user_plot_ajax),
]