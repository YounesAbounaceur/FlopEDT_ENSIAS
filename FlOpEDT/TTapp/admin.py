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




from django.contrib import admin
from base.admin import DepartmentModelAdmin

from TTapp.models import LimitCourseTypePerPeriod, ReasonableDays, Stabilize, \
    MinHalfDays, MinNonPreferedSlot, AvoidBothSlots, SimultaneousCourses

# Register your models here.

# from TTapp.models import TestJour

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, \
    DropdownFilterCho


class LimitCourseTypePerPeriodAdmin(DepartmentModelAdmin):
    list_display = ('week', 
                    'year', 
                    'train_prog', 
                    'type', 
                    'limit', 
                    'period', 
                    'comment')
    ordering = ()
    list_filter = (('train_prog', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutors', DropdownFilterRel),
                   ('type', DropdownFilterRel),
                   )


class ReasonableDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'train_prog', 'comment')
    ordering = ()
    list_filter = (('train_prog', DropdownFilterRel),
                   ('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   )


class StabilizeAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'train_prog', 'general',
                    'group', 'tutor', 'module', 'type', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_prog', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('module', DropdownFilterRel),
                   ('type', DropdownFilterRel),
                   )


class MinHalfDaysAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'train_prog', 'join2courses', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('groups', DropdownFilterRel),
                   ('tutors', DropdownFilterRel),
                   ('modules', DropdownFilterRel),
                   'join2courses',
                   )

    
    def get_field_queryset(self, db, db_field, request):

        queryset = super().get_field_queryset(db, db_field, request)

        if queryset and db_field.name == 'groups':
            return queryset.filter(basic=True).distinct()

        return queryset                          


class MinNonPreferedSlotAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'train_prog', 'tutor', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('tutor', DropdownFilterRel),
                   ('train_prog', DropdownFilterRel),
                   )


class AvoidBothSlotsAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'train_prog', 'tutor', 'group', 'slot1', 'slot2', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('train_prog', DropdownFilterRel),
                   ('tutor', DropdownFilterRel),
                   ('group', DropdownFilterRel),
                   ('slot1', DropdownFilterRel),
                   ('slot2', DropdownFilterRel),
                   )


class SimultaneousCoursesAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'train_prog', 'course1', 'course2', 'comment')
    ordering = ()
    list_filter = (('week', DropdownFilterAll),
                   ('year', DropdownFilterAll),
                   ('course1', DropdownFilterRel),
                   ('course2', DropdownFilterRel),
                   )


admin.site.register(LimitCourseTypePerPeriod, LimitCourseTypePerPeriodAdmin)
admin.site.register(ReasonableDays, ReasonableDaysAdmin)
admin.site.register(Stabilize, StabilizeAdmin)
admin.site.register(MinHalfDays, MinHalfDaysAdmin)
admin.site.register(MinNonPreferedSlot, MinNonPreferedSlotAdmin)
admin.site.register(AvoidBothSlots, AvoidBothSlotsAdmin)
admin.site.register(SimultaneousCourses, SimultaneousCoursesAdmin)
