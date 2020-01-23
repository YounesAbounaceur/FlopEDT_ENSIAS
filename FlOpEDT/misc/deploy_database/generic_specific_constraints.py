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


from TTapp.models import LimitCourseTypePerPeriod, ReasonableDays, MinHalfDays, max_weight, \
    SimultaneousCourses, LimitedSlotChoices
from base.models import Time, Day, TrainingProgramme, CourseType, Module, RoomGroup, Slot, Group, Course, Department
from people.models import Tutor

info=Department.objects.get(abbrev='info')

def add_iut_specific_constraints():
    add_iut_blagnac_basics()
    add_iut_blagnac_specials()
    add_iut_blagnac_lp()
    add_iut_blagnac_other()


def add_iut_blagnac_basics():
    DS = CourseType.objects.get(name='CTRL')
    CM = CourseType.objects.get(name='CM')
    TD = CourseType.objects.get(name='TD')
    TP = CourseType.objects.get(name='TP')

    print("adding IUT Blagnac's basic constraints")
    lp = TrainingProgramme.objects.get(abbrev='APSIO')
    dut1 = TrainingProgramme.objects.get(abbrev='INFO1')
    dut2 = TrainingProgramme.objects.get(abbrev='INFO2')

    sport = Module.objects.get(abbrev='SC', period__name='S1')
    lun_17h = Slot.objects.get(heure__hours=17, jour__day=Day.MONDAY)
    mar_17h = Slot.objects.get(heure__hours=17, jour__day=Day.TUESDAY)

    C, created = LimitedSlotChoices.objects.get_or_create(module=sport, department=info)
    if created:
        C.save()
    C.possible_slots.add(lun_17h)
    C.possible_slots.add(mar_17h)
    C.save()


    # Libérer des demi-journées aux étudiants
    for g in Group.objects.exclude(train_prog=lp):
        M = MinHalfDays(group=g, weight=max_weight, department=info)
        M.save()


def add_iut_blagnac_specials():
    print("adding IUT Blagnac's special constraints")

    DS = CourseType.objects.get(name='CTRL')
    CM = CourseType.objects.get(name='CM')
    TD = CourseType.objects.get(name='TD')
    TP = CourseType.objects.get(name='TP')

    # Pas plus de 2 examens par jour!
    pas_plus_de_2_exams_par_jour = True
    if pas_plus_de_2_exams_par_jour:
        for promo in TrainingProgramme.objects.all():
            L = LimitCourseTypePerPeriod(limit=2, department=info,
                                         type=DS,
                                         period=LimitCourseTypePerPeriod.FULL_DAY,
                                         train_prog=promo)
            L.save()

    # Pas plus de 2 amphis par demie journée
    for semaine in range(1,52,2):
        for promo in TrainingProgramme.objects.all():
            L = LimitCourseTypePerPeriod(limit=2, week=semaine, year=2018,
                                         type=CM, department=info,
                                         period=LimitCourseTypePerPeriod.HALF_DAY,
                                         train_prog=promo)
            L.save()
    # Pas plus d'un amphi par matière et par jour
    for semaine in range(1,52,3):
        for module in Module.objects.all():
            L = LimitCourseTypePerPeriod(limit=1, week=semaine, year=2018,
                                         type=CM, department=info,
                                         period=LimitCourseTypePerPeriod.FULL_DAY,
                                         module=module)
            L.save()


def add_iut_blagnac_lp():
    lp = TrainingProgramme.objects.get(abbrev='APSIO')
    print("adding LP constraints")
    # Avoid first and last slot at the same time for train_prog 3
    R = ReasonableDays(train_prog=lp, department=info,
                       weight=max_weight)
    R.save()

    # Force that only 3 courses are the same HD, and only on 2 HD if 4 courses
    for module in Module.objects.filter(train_prog=lp):
        M = MinHalfDays(module=module, department=info,
                        join2courses=True, weight=max_weight)
        M.save()


def add_iut_blagnac_other():
    DS = CourseType.objects.get(name='CTRL')
    CM = CourseType.objects.get(name='CM')
    TD = CourseType.objects.get(name='TD')
    TP = CourseType.objects.get(name='TP')
    print("finally, adding other constraints")

    # Limit Long Days for instructors
    for i in Tutor.objects.all():
        R = ReasonableDays(tutor=i, department=info,
                           weight=max_weight)
        R.save()

    # Impose pour certains vacataires le fait qu'ils viennent sur une seule demi-journée (si moins de 3 cours)
    # C'EST CETTE CONTRAINTE, LORSQU'ELLE N'EST QUE PREFERENCE, QUI CREE LA PAGAILLE DANS CBC!!!
    for i in Tutor.objects.filter(username__in=['AB', 'AJ', 'CDU', 'FMA', 'GRJ', 'JD', 'SD', 'FMO',
                                                                'JPC', 'MN', 'NJ', 'TC', 'XB', 'PDU', 'VG', 'LC',
                                                                'MTH','YB', 'BB']):
        M = MinHalfDays(tutor=i, department=info,
                        join2courses=True,
                        weight=max_weight)
        M.save()

    # Les séances de réflexion pédagogiques ont lieu à 11h, pour les 2 train_progs en même temps,
    # et le mardi ou mercredi
    cms_peda = Course.objects.filter(module__abbrev='PEDA')
    if cms_peda.count() >= 2:
        S=SimultaneousCourses(course1=cms_peda[0], course2=cms_peda[1], department=info)
        S.save()

add_iut_specific_constraints()
