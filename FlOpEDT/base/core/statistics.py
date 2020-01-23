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

import datetime

from django.db.models import Count
from base.models import ScheduledCourse, RoomGroup, Holiday
from base.core.period_weeks import PeriodWeeks

from people.models import Tutor

def get_holiday_list(period):
    for year, _ in period:
        for holiday in Holiday.objects.filter(year=year):
            yield year, holiday.week, holiday.day.no

def get_room_activity_by_day(department, year=None):

    # Return a array containing each room of a department 
    # with the number of days a room is unoccupied 
    # during a given period. 

    # TODO: If the period is not ended occupancy is 
    # computed until the current week

    # year : correponds to the first period's year
    period = PeriodWeeks(department=department, year=year, exclude_empty_weeks=True)
    period_filter = period.get_filter()
    
    # Get room list 
    rooms = tuple(RoomGroup.objects \
        .filter(types__department = department) \
        .values_list('name', flat=True)
        .distinct())

    # Filter all the scheduled courses for the period
    scheduled = set()
    
    if period_filter:
        scheduled.update(ScheduledCourse.objects \
            .filter(
                period_filter,
                copie_travail=0,
                cours__module__train_prog__department=department) \
            .values_list('room__name', 'cours__an', 'cours__semaine', 'creneau__jour') \
            .distinct())

    # Holiday list
    holiday_list = set(get_holiday_list(period))
    
    # Get the total number of open days
    all_weeks = period.get_weeks()
    nb_open_days = len(all_weeks) * 5

    # Get the number of day per room where the room is not utilized
    unused_days_by_room = []
    for room in rooms:

        # Initialize unused count
        room_context = { 'room': room, 'count': 0}
        unused_days_by_room.append(room_context)

        for current_year, weeks in period:
            for current_week in weeks:
                for week_day in tuple(range(1,6)):

                    # Test if the current day is a holiday
                    if (current_year, current_week, week_day,) in holiday_list:
                        continue
                    
                    # Test if a course has been realised in the 
                    # current room for a given day number
                    room_availability = (room, current_year, current_week, week_day)
                    if not(room_availability in scheduled):
                        room_context['count'] += 1 
        

    return {'open_days':nb_open_days, 'room_activity': unused_days_by_room}


def get_tutor_hours(department, year=None):

    # Return a tutor list with the numbers 
    # of hours of given courses

    # year : correponds to the first period's year
    period = PeriodWeeks(year=year)
    period_filter = period.get_filter(related_path='taught_courses')    
    
    # Filter all the scheduled courses for the period
    # and group by tutor    
    query = Tutor.objects \
        .filter(
            period_filter,
            departments=department,
            taught_courses__scheduledcourse__copie_travail=0,
            ) \
        .values_list('pk', 'username', 'first_name', 'last_name') \
        .annotate(slots=Count('taught_courses__scheduledcourse'))

    return list(query)