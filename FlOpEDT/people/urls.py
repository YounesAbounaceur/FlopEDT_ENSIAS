# -*- coding: utf-8 -*-

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
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from people.student import AddStudent, ChangeStudent
from people.tutor import AddFullStaffTutor, AddSupplyStaffTutor, AddBIATOSTutor
from people.tutor import ChangeFullStaffTutor, ChangeSupplyStaffTutor, ChangeBIATOSTutor
from . import views

app_name="people"

urlpatterns = [
#    url(r'^login', views.login, name="login"),
    url(r'^login/$',
        auth_views.LoginView.as_view(template_name='people/login.html'),
        name='login'),
    url(r'^logout/$',
        auth_views.LogoutView.as_view( next_page= '/'),
        name='logout'),
    url(r'^password-reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='people/password_reset_form.html',
            email_template_name='people/password_reset_email.html',
            subject_template_name='people/password_reset_subject.txt',
            success_url=reverse_lazy('people:password_reset_done')),
        name='password_reset'),
    url(r'^pwd-reset-done/$',
        auth_views.PasswordResetDoneView.as_view(
            template_name='people/password_reset_done.html'),
        name='password_reset_done'),
    url(r'^pwd-reset-complete/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='people/password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^password-change/$',
        auth_views.PasswordChangeView.as_view(
            template_name='people/password_change_form.html',
            success_url=reverse_lazy('people:password_change_done')),
        name='password_change'),
    url(r'^pwd-chg-done/$',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='people/password_change_done.html'),
        name='password_change_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='people/password_reset_confirm.html',
            success_url=reverse_lazy('people:password_reset_complete')),
        name='password_reset_confirm'),
    url(r'^add/some/(?P<kind>[A-Za-z]*)$',
        views.redirect_add_people_kind,
        name="add_redirect"),
    url(r'^add/student/$',
        AddStudent.as_view(),
        name="add_student"),
    url(r'^add/fullstaff/$',
        AddFullStaffTutor.as_view(),
        name="add_fullstaff"),
    url(r'^add/supplystaff/$',
        AddSupplyStaffTutor.as_view(),
        name="add_supplystaff"),
    url(r'^add/biatos/$',
        AddBIATOSTutor.as_view(),
        name="add_BIATOS"),
    url(r'^change/some/$',
        views.redirect_change_people_kind,
        name="change_redirect"),
    url(r'^change/student/$',
        ChangeStudent.as_view(),
        name="change_student"),
    url(r'^change/fullstaff/$',
        ChangeFullStaffTutor.as_view(),
        name="change_fullstaff"),
    url(r'^change/supplystaff/$',
        ChangeSupplyStaffTutor.as_view(),
        name="change_supplystaff"),
    url(r'^change/biatos/$',
        ChangeBIATOSTutor.as_view(),
        name="change_BIATOS"),
	url(r'^fetch_tutors/$',
        views.fetch_tutors,
        name="fetch_tutors"),
    ]
