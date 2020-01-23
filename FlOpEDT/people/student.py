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

from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView

from .forms import AddStudentForm, ChangeStudentForm
from .models import User, Student

class AddStudent(CreateView):
    model = Student
    form_class = AddStudentForm
    template_name = 'people/adduser.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        next = self.request.GET.get('next', 'base:edt')
        return redirect(next)

class ChangeStudent(UpdateView):
    model = Student
    from_class = ChangeStudentForm
    template_name = 'people/changeuser.html'
    fields = ('username', 'email', 'belong_to', )
    success_url = '/'
    
    def get_object(self, queryset=None):
        return self.request.user if self.request.user.is_authenticated else None
         
