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



from base import weeks
from base.models import TrainingProgramme, ScheduledCourse
from base.core.period_weeks import PeriodWeeks
from people.models import FullStaff
from solve_board.models import SolveRun
# from solve_board.consumers import ws_add
from MyFlOp.MyTTModel import MyTTModel
from TTapp.models import TTConstraint
from TTapp.TTModel import get_constraints

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, JsonResponse, HttpResponse
from django.conf import settings
from django.db.models import Q

# from channels import Group

from multiprocessing import Process
from io import StringIO
import os
import sys
import json

from django.template.response import TemplateResponse
from django.conf import settings

import pulp.solvers as pulp_solvers

# String used to specify all filter
text_all='All'


def get_work_copies(department, week):
    """
    Get the list of working copies for a target week
    """
    period_filter = PeriodWeeks().get_filter(week=week)
    work_copies = ScheduledCourse.objects \
                    .filter(
                        period_filter,
                        cours__module__train_prog__department=department) \
                    .values_list('copie_travail', flat=True) \
                    .distinct()     
    
    return list(work_copies)

def get_pulp_solvers(available=True):
    def recurse_solver_hierachy(solvers):
        for s in solvers:
            if available:
                if s().available():
                    yield s
            else:
                yield s

            yield from recurse_solver_hierachy(s.__subclasses__())
    
    solvers = pulp_solvers.LpSolver_CMD.__subclasses__()
    return tuple(recurse_solver_hierachy(solvers))


def get_pulp_solvers_viewmodel():   

    # Build a dictionnary of supported solver 
    # classnames and readable names

    # Get available solvers only on production environment
    solvers = get_pulp_solvers(not settings.DEBUG)
    
    # Get readable solver name from solver class name
    viewmodel = []
    for s in solvers:
        key = s.__name__
        name = key.replace('PULP_', '').replace('_CMD', '')
        viewmodel.append((key, name))

    return viewmodel

def get_constraints_viewmodel(department, **kwargs):
    #
    # Extract simplified datas from constraints instances
    #
    constraints = get_constraints(department, **kwargs)
    return [c.get_viewmodel() for c in constraints]


def get_context(department, year, week, train_prog=None):
    #
    #   Get contextual datas
    #
    params = {'week':int(week), 'year':int(year)}

    # Get constraints
    if train_prog and not train_prog == text_all:
        params.update({'train_prog':train_prog})

    constraints = get_constraints_viewmodel(department, **params)

    # Get working copy list
    work_copies = get_work_copies(department, int(week))

    context = { 
        'constraints': constraints,
        'work_copies': work_copies,
    }

    return context


@staff_member_required
def fetch_context(req, train_prog, year, week, **kwargs):

    context = get_context(req.department, year, week, train_prog)
    return HttpResponse(json.dumps(context), content_type='text/json')


@staff_member_required
def main_board(req, **kwargs):

    department = req.department

    # Get week list
    period = PeriodWeeks(department, exclude_empty_weeks=True)
    week_list = period.get_weeks(format=True)

    # Get solver list
    solvers_viewmodel = get_pulp_solvers_viewmodel()

    # Get all TrainingProgramme
    all_tps = list(TrainingProgramme.objects \
                    .filter(department=department) \
                    .values_list('abbrev', flat=True)) 

    view_context = {
                   'department': department,
                   'text_all': text_all,
                   'weeks': json.dumps(week_list),
                   'train_progs': json.dumps(all_tps),
                   'solvers': solvers_viewmodel,
                   }
    
    # Get contextual datas (constraints, work_copies)
    data_context = get_context(department, year=week_list[0][0], week=week_list[0][1])
    view_context.update({ k:json.dumps(v) for k, v in data_context.items()})
    
    return TemplateResponse(req, 'solve_board/main-board.html', view_context)

