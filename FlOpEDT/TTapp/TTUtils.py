# coding:utf-8

# !/usr/bin/python

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

from base.models import Slot, ScheduledCourse, RoomPreference, EdtVersion, Department
from django.db.models import Max, Q
from TTapp.models import LimitedRoomChoices
from base.views import get_key_course_pl, get_key_course_pp
from django.core.cache import cache

def basic_reassign_rooms(department, semaine, an, target_work_copy):
    """
    Reassign the rooms to minimize moves...
    """
    print("reassigning rooms to minimize moves...")

    scheduled_courses_params = {
        'cours__module__train_prog__department': department,
        'cours__semaine': semaine,
        'cours__an': an,
        'copie_travail': target_work_copy,
    }

    slots = Slot.objects.all().order_by('jour', 'heure')
    for sl in slots:
        rank = list(slots.filter(jour=sl.jour, heure__apm=sl.heure.apm)).index(sl)
        if rank == 0:
            continue
        slots_list = list(slots)
        precedent_sl = slots_list[slots_list.index(sl) - 1]
        nsl = ScheduledCourse.objects.filter(
                                        creneau=sl,
                                        **scheduled_courses_params)
        # print sl
        for CP in nsl:
            precedent = ScheduledCourse \
                .objects \
                .filter(creneau=precedent_sl,
                        cours__room_type=CP.cours.room_type,
                        cours__tutor=CP.cours.tutor,
                        **scheduled_courses_params)
            if len(precedent) == 0:
                precedent = ScheduledCourse \
                    .objects \
                    .filter(
                            creneau=precedent_sl,
                            cours__room_type=CP.cours.room_type,
                            cours__groupe=CP.cours.groupe,
                            **scheduled_courses_params)
                if len(precedent) == 0:
                    continue
            precedent = precedent[0]
            # print "### has prec, trying to reassign:", precedent, "\n\t",
            cp_using_prec = ScheduledCourse \
                .objects \
                .filter(creneau=sl,
                        room=precedent.room,
                        **scheduled_courses_params)
            # test if lucky
            if cp_using_prec.count() == 1 and cp_using_prec[0] == CP:
                # print "lucky, no change needed"
                continue
            # test if precedent.room is available
            prec_is_unavailable = False
            for r in precedent.room.subrooms.all():
                if RoomPreference.objects.filter(semaine=semaine, an=an, creneau=sl, room=r, valeur=0).exists():
                    prec_is_unavailable = True
                
                if ScheduledCourse.objects \
                    .filter(creneau=sl,
                            room__in=r.subroom_of.exclude(id=precedent.room.id),
                            **scheduled_courses_params) \
                    .exists():
                        prec_is_unavailable = True
            
            if prec_is_unavailable:
                # print "room is not available"
                continue
            
            # test if precedent.room is used for course of the same room_type and swap
            if not cp_using_prec.exists():
                CP.room = precedent.room
                CP.save()
                # print "assigned", CP
            elif cp_using_prec.count() == 1:
                sib = cp_using_prec[0]
                if sib.cours.room_type == CP.cours.room_type and sib.cours:
                    if not LimitedRoomChoices.objects.filter(
                                Q(week=semaine) | Q(week=None),
                                Q(year=an) | Q(year=None),
                                Q(train_prog=sib.cours.module.train_prog) | Q(module=sib.cours.module) | Q(group=sib.cours.groupe) |
                                Q(tutor=sib.cours.tutor) | Q(type=sib.cours.type),
                                possible_rooms=sib.room).exists():
                        r = CP.room
                        CP.room = precedent.room
                        sib.room = r
                        CP.save()
                        sib.save()
                    # print "swapped", CP, " with", sib
    cache.delete(get_key_course_pl(department.abbrev,
                                   an,
                                   semaine,
                                   target_work_copy))
    print("done")


def basic_swap_version(department, week, year, copy_a, copy_b=0):

    scheduled_courses_params = {
        'cours__module__train_prog__department': department,
        'cours__semaine': week,
        'cours__an': year,
    }

    try:
        tmp_wc = ScheduledCourse \
                     .objects \
                     .filter(**scheduled_courses_params) \
                     .aggregate(Max('copie_travail'))['copie_travail__max'] + 1
    except KeyError:
        print('No scheduled courses')
        return

    version_copy = EdtVersion.objects.get(department=department, semaine=week, an=year)

    for cp in ScheduledCourse.objects.filter(copie_travail=copy_a, **scheduled_courses_params):
        cp.copie_travail = tmp_wc
        cp.save()

    for cp in ScheduledCourse.objects.filter(copie_travail=copy_b, **scheduled_courses_params):
        cp.copie_travail = copy_a
        cp.save()

    for cp in ScheduledCourse.objects.filter(copie_travail=tmp_wc, **scheduled_courses_params):
        cp.copie_travail = copy_b
        cp.save()

    if copy_a ==0 or copy_b == 0:
        version_copy.version += 1
        version_copy.save()

    cache.delete(get_key_course_pl(department.abbrev,
                                   year,
                                   week,
                                   copy_a))
    cache.delete(get_key_course_pl(department.abbrev,
                                   year,
                                   week,
                                   copy_b))
    cache.delete(get_key_course_pp(department.abbrev,
                                   year,
                                   week,
                                   copy_a))
    cache.delete(get_key_course_pp(department.abbrev,
                                   year,
                                   week,
                                   copy_b))
