from django.urls import path
from django.conf.urls import url

from . import views

app_name="synchro"

urlpatterns = [
    path('', views.index, name="index"),
    url(r'enseignant/(?P<id>\w+)\.ics$', views.tutor, name="tutor"),
    url(r'salle/(?P<id>\w+)\.ics$', views.room, name="room"),
    url(r'groupe/(?P<promo_id>\w+)/(?P<groupe_id>\w+)\.ics$', views.group, name="group")
]
