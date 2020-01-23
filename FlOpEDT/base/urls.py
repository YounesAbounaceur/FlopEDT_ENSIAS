# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from django.conf.urls import url, include
from django.urls import path
from . import views
from . import statistics
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

app_name="base"

urlpatterns = [
    # favicon
    # ----------------------------
    url(views.fav_regexp,
        views.favicon,
        name="favicon"),

    # directly reachable by users
    # ----------------------------
    url(r'^semaine-type$', views.stype, name="stype"),
    url(r'^aide$', views.aide, name="aide"),
    url(r'^decale$', views.decale, name="decale"),    
    url(r'^contact$', views.contact, name="contact"),
    url(r'^((?P<an>\d{4}))?(/(?P<semaine>\d{1,2}))?$', views.edt, name="edt"),
    url(r'^tv(/(?P<semaine>\d+))?(/(?P<an>\d+))?$', views.edt_light, name="edt_light"),

    # exchanges with the db via django
    # ---------------------------------

    # from db to screen
    url(r'^fetch_cours_pl/(?P<year>\d+)/(?P<week>\d+)/(?P<num_copy>\d+)$', views.fetch_cours_pl, name="fetch_cours_pl"),
    url(r'^fetch_cours_pp/(?P<year>\d+)/(?P<week>\d+)/(?P<num_copy>\d+)$', views.fetch_cours_pp, name="fetch_cours_pp"),
    url(r'^fetch_dispos/(?P<year>\d+)/(?P<week>\d+)$', views.fetch_dispos, name="fetch_dispos"),
    url(r'^fetch_stype$', views.fetch_stype, name="fetch_stype"),
    url(r'^fetch_decale$', views.fetch_decale, name="fetch_decale"),
    url(r'^fetch_decale$', statistics.fetch_room_activity, name="fetch_room_activity"),
    url(r'^fetch_bknews/(?P<year>\d+)/(?P<week>\d+)$', views.fetch_bknews, name="fetch_bknews"),
    url(r'^fetch_groups$', views.fetch_groups, name="fetch_groups"),    
    url(r'^fetch_rooms$', views.fetch_rooms, name="fetch_rooms"),    
    url(r'^fetch_unavailable_rooms/(?P<year>\d+)/(?P<week>\d+)$', views.fetch_unavailable_rooms, name="fetch_unavailable_rooms"),
    url(r'^fetch_all_tutors/$', views.fetch_all_tutors, name="fetch_all_tutors"),
    url(r'^fetch_all_versions/$', views.fetch_all_versions, name="fetch_all_versions"),
    url(r'^fetch_week_infos/(?P<year>\d+)/(?P<week>\d+)$', views.fetch_week_infos, name="fetch_week_infos"),

    # statistics
    # ---------------------------------
    path('statistics/', include([
        path('', statistics.index, name="statistics"),
        path('rooms/', statistics.fetch_room_activity, name="room_activity"),
        path('tutors/', statistics.fetch_tutor_hours, name="tutor_hours"),
    ])),

    # from screen to db
    url(r'^change_edt$', views.edt_changes, name="edt_changes"),
    url(r'^change_dispos/$', views.dispos_changes, name="dispos_changes"),
    url(r'^change_decale$', views.decale_changes, name="decale_changes"),


    # predefined
    # ------------
]

# https://pypi.python.org/pypi/django-live-log
# https://github.com/abdullatheef/django_live_log
