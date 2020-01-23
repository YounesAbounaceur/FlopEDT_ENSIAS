# coding:utf-8

# !/usr/bin/python3

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
import functools

from TTapp.TTUtils import basic_reassign_rooms, basic_swap_version
from base.models import Department

def resolve_department(func):
    
    # Replace department attribute by the target 
    # department instance if needed

    @functools.wraps(func)
    def _wraper_function(department, *args, **kwargs):

        if type(department) is str:
            department = Department.objects.get(abbrev=department)

        func(department, *args, **kwargs)

    return _wraper_function


@resolve_department
def reassign_rooms(department, week, year, target_work_copy):
    basic_reassign_rooms(department, week, year, target_work_copy)

@resolve_department
def swap_version(department, week, year, copy_a, copy_b=0):
    basic_swap_version(department, week, year, copy_a, copy_b)
