# coding: utf8
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

from base.models import Time, Day, Slot

from django.core.exceptions import ObjectDoesNotExist


def assign_day_time_numbers():
    # Days
    for no in range(len(Day.CHOICES)):
        try:
            d = Day.objects.get(day=Day.CHOICES[no][0])
            d.no = no
            d.save()
        except ObjectDoesNotExist:
            pass

    # Times
    l = Time.objects.order_by('hours', 'minutes')
    for no in range(len(l)):
        l[no].no = no
        l[no].save()

    # Check slots
    for d in Day.CHOICES:
        slot_list = Slot.objects \
                        .filter(jour__day=d[0]) \
                        .order_by('heure__hours', 'heure__minutes')
        for si in range(len(slot_list) - 1):
            prev_sl = slot_list[si]
            next_sl = slot_list[si + 1]
            if prev_sl.heure.hours*60 + prev_sl.heure.minutes + prev_sl.duration \
               > next_sl.heure.hours*60 + next_sl.heure.minutes :
                raise Exception("Intersection between slot %s and %s is non empty" % prev_sl, next_sl)

        
