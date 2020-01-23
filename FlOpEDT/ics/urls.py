from django.urls import path
from ics.feeds import TutorEventFeed, RoomEventFeed, GroupEventFeed

from ics import views

app_name = 'ics'

urlpatterns = [
    path(r'', views.index, name="index"),
    path(r'tutor/<slug:tutor>.ics', TutorEventFeed(), name="tutor"),
    path(r'room/<slug:room>.ics', RoomEventFeed(), name="room"),
    path(r'group/<slug:training_programme>/<slug:group>.ics', GroupEventFeed(), name="group")
]
