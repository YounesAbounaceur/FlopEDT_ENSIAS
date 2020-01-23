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

import logging

from django.core.exceptions import ObjectDoesNotExist

from base.models import Group, TrainingProgramme, \
                        GroupDisplay, TrainingProgrammeDisplay, \
                        ScheduledCourse, EdtVersion, Department, Regen

from base.models import Room, RoomType, RoomGroup, \
                        RoomSort, Period, CourseType, \
                        BreakingNews, TutorCost, GroupType

from people.models import Tutor

from TTapp.models import TTConstraint


logger = logging.getLogger(__name__)


def create_first_department():    

    department = Department.objects.create(name="Default Department", abbrev="default")
    
    # Update all existing department related models
    models = [
        TrainingProgramme, EdtVersion, Regen, \
        RoomType, Period, CourseType, BreakingNews, \
        TutorCost, GroupType]
   
    for model in models:
        model.objects.all().update(department=department)

    # Update all ManyToMany relations with Department
    models = [Tutor]
    for model in models:
        for model_class in model.objects.all():
            model_class.departments.add(department)

    # Update existing Constraint
    types = TTConstraint.__subclasses__()

    for type in types:
        type.objects.all().update(department=department)
    
    return department


def get_edt_version(department, week, year, create=False):

    params = {'semaine': week, 'an': year, 'department': department}

    if create:
        try:
            edt_version, _ = EdtVersion.objects.get_or_create(defaults={'version': 0}, **params)
        except EdtVersion.MultipleObjectsReturned as e:
            logger.error(f'get_edt_version: database inconsistency, multiple objects returned for {params}')
            raise(e)
        else:    
            version = edt_version.version
    else:
        """
        Raise model.DoesNotExist to simulate get behaviour 
        when no item is matching filter parameters
        """
        try:
            version = EdtVersion.objects.filter(**params).values_list("version", flat=True)[0]   
        except IndexError:
            raise(EdtVersion.DoesNotExist)
    return version


def get_scheduled_courses(department, week, year, num_copy):

    qs = ScheduledCourse.objects \
                    .filter(
                        cours__module__train_prog__department=department,
                        cours__semaine=week,
                        cours__an=year,
                        copie_travail=num_copy)
    return qs    


def get_groups(department_abbrev):
    """
    Return the groups hierachical representation from database
    """
    final_groups = []

    # Filter TrainingProgramme by department
    training_program_query = TrainingProgramme.objects.filter(department__abbrev=department_abbrev)

    for train_prog in training_program_query:

        gp_dict_children = {}
        gp_master = None
        for gp in Group.objects.filter(train_prog=train_prog):
            if gp.full_name() in gp_dict_children:
                raise Exception('Group name should be unique')
            if gp.parent_groups.all().count() == 0:
                if gp_master is not None:
                    raise Exception('One single group is able to be without '
                                    'parents')
                gp_master = gp
            elif gp.parent_groups.all().count() > 1:
                raise Exception('Not tree-like group structures are not yet '
                                'handled')
            gp_dict_children[gp.full_name()] = []

        for gp in Group.objects.filter(train_prog=train_prog):
            for new_gp in gp.parent_groups.all():
                gp_dict_children[new_gp.full_name()].append(gp)

        final_groups.append(get_descendant_groups(gp_master, gp_dict_children))

    return final_groups


def get_descendant_groups(gp, children):
    """
    Gather informations about all descendants of a group gp
    :param gp:
    :param children: dictionary <group_full_name, list_of_children>
    :return: an object containing the informations on gp and its descendants
    """
    current = {}
    if not gp.parent_groups.all().exists():
        current['parent'] = 'null'
        tp = gp.train_prog
        current['promo'] = tp.abbrev
        try:
            tpd = TrainingProgrammeDisplay.objects.get(training_programme=tp)
            if tpd.short_name != '':
                current['promotxt'] = tpd.short_name
            else:
                current['promotxt'] = tp.abbrev
            current['row'] = tpd.row
        except ObjectDoesNotExist:
            raise Exception('You should indicate on which row a training '
                            'programme will be displayed '
                            '(cf TrainingProgrammeDisplay)')
    current['name'] = gp.nom
    try:
        gpd = GroupDisplay.objects.get(group=gp)
        if gpd.button_height is not None:
            current['buth'] = gpd.button_height
        if gpd.button_txt is not None:
            current['buttxt'] = gpd.button_txt
    except ObjectDoesNotExist:
        pass

    if len(children[gp.full_name()]) > 0:
        current['children'] = []
        for gp_child in children[gp.full_name()]:
            gp_obj = get_descendant_groups(gp_child, children)
            gp_obj['parent'] = gp.nom
            current['children'].append(gp_obj)

    return current


def get_rooms(department_abbrev):
    """
    From the data stored in the database, fill the room description file, that
    will be used by the website
    :return:
    """
    dic_rt = {}
    for rt in RoomType.objects.filter(department__abbrev=department_abbrev):
        dic_rt[str(rt)] = []
        for rg in rt.members.all():
            if str(rg) not in dic_rt[str(rt)]:
                dic_rt[str(rt)].append(str(rg))

    dic_rg = {}
    for rg in RoomGroup.objects.all():
        dic_rg[str(rg)] = []
        for r in rg.subrooms.all():
            dic_rg[str(rg)].append(str(r))

    return {'roomtypes':dic_rt,
            'roomgroups':dic_rg}
