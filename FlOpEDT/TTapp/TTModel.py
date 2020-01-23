#!/usr/bin/env python3
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



from pulp import LpVariable, LpConstraint, LpBinary, LpConstraintEQ, \
    LpConstraintGE, LpConstraintLE, LpAffineExpression, LpProblem, LpStatus, \
    LpMinimize, lpSum, LpStatusOptimal, LpStatusNotSolved

from pulp import GUROBI_CMD, PULP_CBC_CMD

from base.models import Slot, Group, Day, Time, \
    Room, RoomGroup, RoomSort, RoomType, RoomPreference, \
    Course, ScheduledCourse, UserPreference, CoursePreference, \
    Department, Module, TrainingProgramme, CourseType, \
    Dependency, TutorCost, GroupFreeHalfDay, GroupCost, Holiday, TrainingHalfDay

from people.models import Tutor

from base.weeks import annee_courante

from TTapp.models import MinNonPreferedSlot, max_weight, Stabilize, TTConstraint

from MyFlOp.MyTTUtils import reassign_rooms

import signal

from django.conf import settings
from django.db.models import Q, Max

import datetime

import logging
logger = logging.getLogger(__name__)

class WeekDB(object):
    def __init__(self, department, week, year, train_prog):
        self.train_prog = train_prog
        self.week = week
        self.year = year
        
        # TIME
        self.days = Day.objects.all()
        self.slots = Slot.objects.all().order_by('jour', 'heure')
        
        # Build a week representation containing slots lists grouped by 
        # day and half-day. (i.e : {(Day, Half-Day): [Slot1, Slot2]})
        self.slots_by_days = {}
        for day in self.days:
            for apm in [Time.AM, Time.PM]:
                apm_slots = [s for s in self.slots if s.heure.apm == apm and s.jour == day]
                self.slots_by_days.update({(day, apm,): apm_slots})
        
        # ROOMS
        self.room_types = RoomType.objects.filter(department=department)
        self.room_groups = RoomGroup.objects.filter(types__department=department).distinct()
        self.rooms = Room.objects.filter(subroom_of__types__department=department).distinct()
        self.room_prefs = RoomSort.objects.filter(for_type__department=department)
              
        self.room_groups_for_type = {t:t.members.all() for t in self.room_types}
        
        # COURSES
        self.courses = Course.objects.filter(
            semaine=week, an=year,
            groupe__train_prog__in=self.train_prog)
        
        self.sched_courses = ScheduledCourse \
            .objects \
            .filter(cours__semaine=week,
                    cours__an=year,
                    cours__groupe__train_prog__in=self.train_prog)
        
        self.fixed_courses = ScheduledCourse.objects \
            .filter(cours__groupe__train_prog__department=department,
                    cours__semaine=week,
                    cours__an=year,
                    copie_travail=0) \
            .exclude(cours__groupe__train_prog__in=self.train_prog)

        self.courses_availabilities = CoursePreference.objects \
            .filter(train_prog__department=department,
                    semaine=week,
                    an=year)
      
        self.modules = Module.objects \
            .filter(id__in=self.courses.values_list('module_id').distinct())
        
        self.dependencies = Dependency.objects.filter(
            cours1__semaine=week,
            cours1__an=year,
            cours2__semaine=week,
            cours1__groupe__train_prog__in=self.train_prog)
       
        # GROUPS
        self.groups = Group.objects.filter(train_prog__in=self.train_prog)
        
        self.basic_groups = self.groups \
            .filter(basic=True)
                    # ,
                    # id__in=self.courses.values_list('groupe_id').distinct())
        
        self.basic_groups_surgroups = {}
        for g in self.basic_groups:
            self.basic_groups_surgroups[g] = [g] + list(g.ancestor_groups())
        
        self.courses_for_group = {}
        for g in self.groups:
            self.courses_for_group[g] = self.courses.filter(groupe=g)
        
        self.holidays = Holiday.objects.filter(week=week, year=year)
        
        self.training_half_days = TrainingHalfDay.objects.filter(
            week=week,
            year=year,
            train_prog__in=self.train_prog)

        # USERS
        self.instructors = Tutor.objects \
            .filter(id__in=self.courses.values_list('tutor_id').distinct())
        
        self.courses_for_tutor = {}
        for i in self.instructors:
            self.courses_for_tutor[i] = self.courses.filter(tutor=i)
        
        self.courses_for_supp_tutor = {}
        for i in self.instructors:
            self.courses_for_supp_tutor[i] = i.courses_as_supp.filter(id__in=self.courses)

        self.availabilities = UserPreference.objects \
                                .filter(semaine=week,
                                    an=year)

class TTModel(object):
    def __init__(self, department_abbrev, semaine, an,
                 train_prog=None,
                 stabilize_work_copy=None,
                 min_nps_i=1.,
                 min_bhd_g=1.,
                 min_bd_i=1.,
                 min_bhd_i=1.,
                 min_nps_c=1.,
                 max_stab=5.,
                 lim_ld=1.):
        print("\nLet's start week #%g" % semaine)
        # beg_file = os.path.join('logs',"FlOpTT")
        self.model = LpProblem("FlOpTT", LpMinimize)
        self.min_ups_i = min_nps_i
        self.min_bhd_g = min_bhd_g
        self.min_bd_i = min_bd_i
        self.min_bhd_i = min_bhd_i
        self.min_ups_c = min_nps_c
        self.max_stab = max_stab
        self.lim_ld = lim_ld
        self.var_nb = 0
        self.semaine = semaine
        self.an = an
        self.warnings={}

        self.department=Department.objects.get(abbrev=department_abbrev)
        if train_prog is None:
            train_prog = TrainingProgramme.objects.filter(department=self.department)
        try:
            _ = iter(train_prog)
        except TypeError:
            train_prog = [train_prog]
        self.train_prog = train_prog
        self.stabilize_work_copy = stabilize_work_copy
        self.wdb = WeekDB(self.department, semaine, an, self.train_prog)
        self.obj = self.lin_expr()
        self.cost_I = dict(list(zip(self.wdb.instructors,
                               [self.lin_expr() for _ in self.wdb.instructors])))
        self.FHD_G = {}
        for apm in [Time.AM, Time.PM]:
            self.FHD_G[apm] = dict(
                list(zip(self.wdb.basic_groups,
                    [self.lin_expr() for _ in self.wdb.basic_groups])))
        
        self.cost_SL = dict(list(zip(self.wdb.slots,
                                [self.lin_expr() for _ in self.wdb.slots])))
        self.cost_G = dict(
            list(zip(self.wdb.basic_groups,
                [self.lin_expr() for _ in self.wdb.basic_groups])))
        
        self.TT = {}
        self.TTrooms = {}
        for sl in self.wdb.slots:
            for c in self.wdb.courses:
                # print c, c.room_type
                self.TT[(sl, c)] = self.add_var("TT(%s,%s)" % (sl, c))
                for rg in self.wdb.room_groups_for_type[c.room_type]:
                    self.TTrooms[(sl, c, rg)] \
                        = self.add_var("TTroom(%s,%s,%s)" % (sl, c, rg))

        self.IBD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                self.IBD[(i, d)] = self.add_var("IBD(%s,%s)" % (i, d))
                # Linking the variable to the TT
                dayslots = self.wdb.slots.filter(jour=d)
                card = 2 * len(dayslots)
                expr = self.lin_expr()
                expr += card * self.IBD[(i, d)]
                for c in self.wdb.courses_for_tutor[i]:
                    for sl in dayslots:
                        expr -= self.TT[(sl, c)]
                self.add_constraint(expr, '>=', 0)

                if self.wdb.fixed_courses.filter(cours__tutor=i,
                                                 creneau__jour=d):
                    self.add_constraint(self.IBD[(i, d)], '==', 1)
                    # This next constraint impides to force IBD to be 1
                    # (if there is a meeting, for example...)
                    # self.add_constraint(expr, '<=', card-1)

        self.IBD_GTE = []
        max_days = 5
        for j in range(max_days + 1):
            self.IBD_GTE.append({})

        for i in self.wdb.instructors:
            for j in range(2, max_days + 1):
                self.IBD_GTE[j][i] = self.add_floor(
                    str(i) + str(j),
                    self.sum(self.IBD[(i, d)] for d in self.wdb.days),
                    j,
                    max_days)

        self.IBHD = {}
        for i in self.wdb.instructors:
            for d in self.wdb.days:
                # add constraint linking IBHD to TT
                for apm in [Time.AM, Time.PM]:
                    self.IBHD[(i, d, apm)] \
                        = self.add_var("IBHD(%s,%s,%s)" % (i, d, apm))
                    halfdayslots = self.wdb.slots.filter(jour=d,
                                                         heure__apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * self.IBHD[(i, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.courses_for_tutor[i]:
                            expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0)
                    # This constraint impides to force IBHD to be 1
                    # (if there is a meeting, for example...)
                    if self.wdb.fixed_courses.filter(cours__tutor=i,
                                                     creneau__jour=d,
                                                     creneau__heure__apm=apm):
                        self.add_constraint(self.IBHD[(i, d, apm)], '==', 1)
                    else:
                        self.add_constraint(expr, '<=', card - 1)

        self.GBHD = {}
        for g in self.wdb.basic_groups:
            for d in self.wdb.days:
                # add constraint linking IBD to EDT
                for apm in [Time.AM, Time.PM]:
                    self.GBHD[(g, d, apm)] \
                        = self.add_var("GBHD(%s,%s,%s)" % (g, d, apm))
                    halfdayslots = self.wdb.slots.filter(jour=d,
                                                         heure__apm=apm)
                    card = 2 * len(halfdayslots)
                    expr = self.lin_expr()
                    expr += card * self.GBHD[(g, d, apm)]
                    for sl in halfdayslots:
                        for c in self.wdb.courses_for_group[g]:
                            expr -= self.TT[(sl, c)]
                        for sg in g.ancestor_groups():
                            for c in self.wdb.courses_for_group[sg]:
                                expr -= self.TT[(sl, c)]
                    self.add_constraint(expr, '>=', 0)
                    self.add_constraint(expr, '<=', card - 1)

        self.avail_instr, self.unp_slot_cost \
            = self.compute_non_prefered_slot_cost()

        self.unp_slot_cost_course, self.avail_course \
            = self.compute_non_prefered_slot_cost_course()

        # Hack : permet que ça marche même si les dispos sur la base sont pas complètes
        for i in self.wdb.instructors:
            for sl in self.wdb.slots:
                if sl not in self.avail_instr[i]:
                    self.avail_instr[i][sl] = 0
                if sl not in self.unp_slot_cost[i]:
                    self.unp_slot_cost[i][sl] = 0

        self.add_TT_constraints()

        self.update_objective()

        if self.warnings:
            print("Relevant warnings :")
            for key, key_warnings in self.warnings.items():
                print("%s : %s" % (key, ", ".join([str(x) for x in key_warnings])))

        if settings.DEBUG:
            self.model.writeLP('FlOpEDT.lp')

    def add_var(self, name):
        """
        Create a PuLP binary variable
        """
        # return LpVariable(name, lowBound = 0, upBound = 1, cat = LpBinary)
        countedname = name + '_' + str(self.var_nb)
        self.var_nb += 1
        return LpVariable(countedname, cat=LpBinary)

    def add_constraint(self, expr, relation, value, name=None):
        """
        Add a constraint to the model
        """
        if relation == '==':
            pulp_relation = LpConstraintEQ
        elif relation == '<=':
            pulp_relation = LpConstraintLE
        elif relation == '>=':
            pulp_relation = LpConstraintGE
        else:
            raise Exception("relation must be either '==' or '>=' or '<='")

        self.model += LpConstraint(e=expr, sense=pulp_relation,
                                   rhs=value, name=name)

    def lin_expr(self, expr=None):
        return LpAffineExpression(expr)

    def sum(self, *args):
        return lpSum(list(*args))

    def check_and_sum(self, dict, *args):
        """
        This helper method get a variable list check if the corresponding 
        expression exists in the given dict and returns the lpSum of 
        available expressions
        """
        expressions =  [dict(v) for v in args if v in dict]
        return lpSum(expressions)


    def get_var_value(self, ttvar):
        return round(ttvar.value())

    def get_expr_value(self, ttexpr):
        return ttexpr.value()

    def get_obj_coeffs(self):
        """
        get the coeff of each var in the objective
        """
        l = [(weight, var) for (var, weight) in self.obj.items()
             if var.value() != 0 and round(weight) != 0]
        l.sort(reverse=True)
        return l

    def set_objective(self, obj):
        self.model.setObjective(obj)

    def get_constraint(self, name):
        return self.model.constraints[name]

    def get_all_constraints(self):
        return self.model.constraints

    def remove_constraint(self, constraint_name):
        del self.model.constraints[constraint_name]

    def var_coeff(self, var, constraint):
        return constraint[var]

    def change_var_coeff(self, var, constraint, newvalue):
        constraint[var] = newvalue

    def add_conjunct(self, v1, v2):
        """
        Crée une nouvelle variable qui est la conjonction des deux
        et l'ajoute au modèle
        """
        l_conj_var = self.add_var("%s AND %s" % (str(v1), str(v2)))
        self.add_constraint(l_conj_var - (v1 + v2), '>=', -1)
        self.add_constraint(2 * l_conj_var - (v1 + v2) , '<=', 0)
        return l_conj_var

    def add_floor(self, name, expr, floor, bound):
        """
        Add a variable that equals 1 if expr >= floor, is integer expr is
        known to be within [0, bound]
        """
        l_floor = self.add_var("FLOOR %s %d" % (name, floor))
        self.add_constraint(expr - l_floor * floor, '>=', 0)
        self.add_constraint(l_floor * bound - expr, '>=', 1 - floor)
        return l_floor

    def add_to_slot_cost(self, slot, cost):
        self.cost_SL[slot] += cost

    def add_to_inst_cost(self, instructor, cost):
        self.cost_I[instructor] += cost

    def add_to_group_cost(self, group, cost):
        self.cost_G[group] += cost

    def add_warning(self, key, warning):
        if key in self.warnings:
            self.warnings[key].append(warning)
        else:
            self.warnings[key]=[warning]

    def add_stabilization_constraints(self):
        if len(self.train_prog) < TrainingProgramme.objects.count():
            print('Will modify only courses of training programme(s)', self.train_prog)

        # maximize stability
        if self.stabilize_work_copy is not None:
            s = Stabilize(general=True,
                          work_copy=self.stabilize_work_copy)
            s.save()
            s.enrich_model(self, self.max_stab)
            s.delete()
            print('Will stabilize from remote work copy #', \
                self.stabilize_work_copy)
        else:
            print('No stabilization')

    def add_core_constraints(self):
        """
        Add the core constraints to the PuLP model :
            - a course is scheduled once and only once
            - no group has two courses in parallel
            - + a teacher does not have 2 courses in parallel
              + the teachers are available on the chosen slots
            - no course on vacation days
        """

        print("adding core constraints")

        # a course is scheduled once and only once
        for c in self.wdb.courses:
            name = 'core_course_' + str(c) + "_" + str(c.id)
            self.add_constraint(
                self.sum([self.TT[(sl, c)] for sl in self.wdb.slots]),
                '==',
                1,
                name=name)

        # no group has two courses in parallel
        for sl in self.wdb.slots:
            for g in self.wdb.basic_groups:
                expr = self.lin_expr()
                for sg in self.wdb.basic_groups_surgroups[g]:
                    for c in self.wdb.courses_for_group[sg]:
                        expr += self.TT[(sl, c)]
                name = 'core_group_' + g.full_name() + '_' + str(sl)
                self.add_constraint(expr, '<=', 1, name=name)

        # no teacher have 2 courses in parallel
        # teachers are available on the chosen slots
        for sl in self.wdb.slots:
            for i in self.wdb.instructors:
                if self.wdb.fixed_courses.filter(cours__tutor=i, creneau=sl):
                    name = 'fixed_course_tutor_' + str(i) + '_' + str(sl)
                    instr_courses = self.wdb.courses_for_tutor[i]
                    self.add_constraint(
                        self.sum(self.TT[(sl, c)] for c in instr_courses),
                        '==',
                        0,
                        name=name)
                else:
                    expr = self.lin_expr()
                    for c in self.wdb.courses_for_tutor[i]:
                        expr += self.TT[(sl, c)]
                    for c in self.wdb.courses_for_supp_tutor[i]:
                        expr += self.TT[(sl, c)]
                    name = 'core_tutor_' + str(i) + '_' + str(sl)
                    self.add_constraint(expr,
                                        '<=',
                                        self.avail_instr[i][sl],
                                        name=name)

        # Holidays
        for holiday in self.wdb.holidays:
            holislots = self.wdb.slots.filter(jour=holiday.jour)
            if holiday.apm is not None:
                holislots = holislots.filter(heure__apm=holiday.apm)
            for sl in holislots:
                for c in self.wdb.courses:
                    self.add_constraint(self.TT[(sl, c)], '==', 0)

        # Training half day
        for training_half_day in self.wdb.training_half_days:
            training_slots = self.wdb.slots.filter(jour=training_half_day.jour)
            if training_half_day.apm is not None:
                training_slots = training_slots.filter(heure__apm=training_half_day.apm)
            training_progs = self.train_prog
            if training_half_day.train_prog is not None:
                training_progs = [training_half_day.train_prog]
            for sl in training_slots:
                for c in self.wdb.courses.filter(group__train_prog__in=training_progs):
                    self.add_constraint(self.TT[(sl, c)], '==', 0)


    def add_rooms_constraints(self):
        print("adding room constraints")
        # constraint Rooms : there are enough rooms of each type for each slot
        # for each Room, first build the list of courses that may use it
        room_course_compat = {}
        for r in self.wdb.rooms:
            # print "compat for ", r
            room_course_compat[r] = []
            for rg in r.subroom_of.all():
                room_course_compat[r].extend(
                    [(c, rg) for c in
                     self.wdb.courses.filter(room_type__in=rg.types.all())])

        course_rg_compat = {}
        for c in self.wdb.courses:
            course_rg_compat[c] = c.room_type.members.all()

        for sl in self.wdb.slots:
            # constraint : each course is assigned to a RoomGroup
            for c in self.wdb.courses:
                name = 'core_roomtype_' + str(r) + '_' + str(sl)
                self.add_constraint(
                    self.sum(self.TTrooms[(sl, c, rg)] for rg in
                                 course_rg_compat[c]) - self.TT[(sl, c)], '==', 0)

            # constraint : fixed_courses rooms are not available
            for rg in self.wdb.room_groups:
                if self.wdb.fixed_courses.filter(room=rg, creneau=sl).exists():
                    for r in rg.subrooms.all():
                        name = 'fixed_room' + str(r) + '_' + str(sl)
                        self.add_constraint(self.sum(self.TTrooms[(sl, c, room)] for c in 
                                            self.wdb.courses for room in
                                            course_rg_compat[c] if r in room.subrooms.all()), '==', 0, name=name)

            # constraint : each Room is only used once and only when available
            for r in self.wdb.rooms:
                # if sl == self.wdb.slots[0]:
                #     print "R", r, quicksum(self.TTrooms[(sl, c, rg)] \
                # for (c, rg) in room_course_compat[r])
                if RoomPreference.objects \
                    .filter(semaine=self.semaine,
                        an=self.an,
                        creneau=sl,
                        room=r, valeur=0).exists():
                    limit = 0
                else:
                    limit = 1

                # print "limit=",limit,".",
                self.add_constraint(
                    self.sum(self.TTrooms[(sl, c, rg)]
                             for (c, rg) in room_course_compat[r]),
                    '<=',
                    limit,
                    name='core_room_' + str(r) + '_' + str(sl))
            # constraint : respect preference order,
            # if preferred room is available
            for rp in self.wdb.room_prefs:
                e = self.sum(
                    self.TTrooms[(sl, c, rp.unprefer)]
                    for c in self.wdb.courses.filter(room_type=rp.for_type))
                preferred_is_unavailable = False
                for r in rp.prefer.subrooms.all():
                    if RoomPreference.objects.filter(
                            semaine=self.semaine,
                            an=self.an,
                            creneau=sl,
                            room=r, valeur=0).exists():
                        # print r, "unavailable for ",sl
                        preferred_is_unavailable = True
                        break
                    e -= self.sum(self.TTrooms[(sl, c, rg)] for (c, rg) in
                                  room_course_compat[r])
                if preferred_is_unavailable:
                    continue
                # print "### slot :", sl, rp.unprefer, "after", rp.prefer
                # print e <= 0
                self.add_constraint(
                    e,
                    '<=',
                    0
                )

    # constraint : respect preference order with full order for each room type :
    # perfs OK
    # for rt in self.wdb.room_types:
    #     l=[]
    #     for rgp in rt.members.all():
    #         if len(l)>0:
    #             for rgp_before in l:
    #                 e = quicksum(self.TTrooms[(sl, c, rgp)]
    #                              for c in self.wdb.courses.filter(room_type=rt))
    #                 preferred_is_unavailable = False
    #                 for r in rgp_before.subrooms.all():
    #                     if len(db.RoomUnavailability.objects.filter(
    #                                   semaine=self.semaine, an=self.an,
    #                                   creneau=sl, room=r)) > 0:
    #                         # print r, "unavailable for ",sl
    #                         preferred_is_unavailable = True
    #                         break
    #                     e -= quicksum(self.TTrooms[(sl, c, rg)] for (c, rg) in
    #                                   room_course_compat[r])
    #                 if preferred_is_unavailable:
    #                     continue
    #                 self.add_constraint(
    #                     e,
    #                     GRB.LESS_EQUAL,
    #                     0
    #                 )
    #         l.append(rgp)

    def add_dependency_constraints(self, weight=None):
        """
        Add the constraints of dependency saved on the DB:
        -include dependencies
        -include non same-day constraint
        -include simultaneity (double dependency)
        If there is a weight, it's a preference, else it's a constraint...
        """
        print('adding dependency constraints')
        for p in self.wdb.dependencies:
            c1 = p.cours1
            c2 = p.cours2
            slots_list=list(self.wdb.slots)
            for sl1 in self.wdb.slots:
                for sl2 in self.wdb.slots:
                    if (p.ND and (sl2.jour == sl1.jour))\
                            or (p.successifs and (slots_list.index(sl2) != slots_list.index(sl1) + 1
                                                  or sl2.jour != sl1.jour)) \
                            or (slots_list.index(sl2) < slots_list.index(sl1)):
                        if not weight:
                            self.add_constraint(self.TT[(sl1, c1)]
                                                + self.TT[(sl2, c2)], '<=', 1)
                        else:
                            conj_var = self.add_conjunct(self.TT[(sl1, c1)],
                                                         self.TT[(sl2, c2)])
                            self.obj += conj_var * weight
                    if (p.successifs and slots_list.index(sl2) == slots_list.index(sl1) + 1
                                                  and sl2.jour == sl1.jour):
                        for rg1 in self.wdb.room_groups_for_type[c1.room_type]:
                            for rg2 in self.wdb.room_groups_for_type[c2.room_type].exclude(id=rg1.id):
                                self.add_constraint(self.TTrooms[(sl1, c1, rg1)]
                                                    + self.TTrooms[(sl2, c2, rg2)], '<=', 1)

    def compute_non_prefered_slot_cost(self):
        """
        Returns:
            - UnpSlotCost : a 2 level-dictionary
                            { teacher => slot => cost (float in [0,1])}}
            - availInstr : a 2 level-dictionary { teacher => slot => 0/1 }

        The slot cost will be:
            - 0 if it is a prefered slot
            - max(0., 2 - slot value / (average of slot values) )
        """

        avail_instr = {}
        unp_slot_cost = {}
        # dict(zip(instructors,
        #          [dict(zip(mm.disponibilite.objects.filter(),[for sl in ]))
        #           for i in instructors]))
        # unpreferred slots for an instructor costs
        # min((float(nb_avail_slots) / min(2*nb_teaching_slots,22)),1)
        for i in self.wdb.instructors:
            nb_teaching_slots = len(self.wdb.courses_for_tutor[i])
            avail_instr[i] = {}
            unp_slot_cost[i] = {}
            if self.wdb.availabilities.filter(user=i):
                availabilities = self.wdb.availabilities.filter(user=i)
            else:
                availabilities = UserPreference \
                    .objects \
                    .filter(user=i,
                            semaine=None)

            if not availabilities.exists():
                self.add_warning(i,"no availability information given")
                for slot in self.wdb.slots:
                    unp_slot_cost[i][slot] = 0
                    avail_instr[i][slot] = 1

            else:
                nb_avail_slots = len(availabilities.filter(valeur__gte=1))
                maximum = max([a.valeur for a in availabilities])
                nb_non_prefered_slots = len(
                    availabilities.filter(valeur__gte=1,
                                          valeur__lte=maximum - 1))

                if nb_avail_slots < nb_teaching_slots:
                    self.add_warning(i, "%g available slots < %g courses"% (nb_avail_slots, nb_teaching_slots))
                    for a in availabilities:
                        avail_instr[i][a.creneau] = 1
                        if a.valeur >= 1:
                            unp_slot_cost[i][a.creneau] = 0
                        else:
                            unp_slot_cost[i][a.creneau] = 1

                elif all(self.wdb.holidays.filter(day=x.creneau.jour).exists()
                         for x in availabilities.filter(valeur__gte=1)):
                    self.add_warning(i, "availabilities only on vacation days!")
                    for a in availabilities:
                        avail_instr[i][a.creneau] = 1
                        if a.valeur >= 1:
                            unp_slot_cost[i][a.creneau] = 0
                        else:
                            unp_slot_cost[i][a.creneau] = 1

                else:
                    moyenne = 0.
                    for a in availabilities:
                        if a.valeur == 0:
                            avail_instr[i][a.creneau] = 0
                        elif a.valeur == maximum:
                            avail_instr[i][a.creneau] = 1
                        else:
                            avail_instr[i][a.creneau] = 1
                            moyenne += a.valeur
                    if nb_non_prefered_slots == 0:
                        moyenne = 1.0 * maximum
                    else:
                        moyenne /= nb_non_prefered_slots

                    if nb_teaching_slots < 9 \
                            and nb_avail_slots < 2 * nb_teaching_slots:
                        self.add_warning(i, "only %g available slots dispos for %g courses" % (nb_avail_slots,\
                                 nb_teaching_slots))
                        for a in availabilities:
                            unp_slot_cost[i][a.creneau] = 0
                    else:
                        for a in availabilities:
                            if a.valeur == maximum or a.valeur == 0:
                                unp_slot_cost[i][a.creneau] = 0
                            else:
                                unp_slot_cost[i][a.creneau] = \
                                    max(0., 2 - a.valeur / moyenne)

        return avail_instr, unp_slot_cost

    def compute_non_prefered_slot_cost_course(self):
        """
         :returns
         non_prefered_slot_cost_course :a 2 level dictionary
         { (CourseType, TrainingProgram)=> { Non-prefered slot => cost (float in [0,1])}}

         avail_course : a 2 level-dictionary
         { (CourseType, TrainingProgram) => slot => availability (0/1) }
        """

        non_prefered_slot_cost_course = {}
        avail_course = {}
        for course_type in CourseType.objects.all():
            for promo in self.train_prog:
                avail_course[(course_type, promo)] = {}
                non_prefered_slot_cost_course[(course_type, promo)] = {}
                courses_avail = self.wdb \
                    .courses_availabilities \
                    .filter(course_type=course_type, train_prog=promo)
                if not courses_avail.exists():
                    courses_avail = CoursePreference.objects \
                        .filter(course_type=course_type,
                                train_prog=promo,
                                semaine=None,
                                an=annee_courante)
                if not courses_avail.exists():
                    print("No course availability given for %s - %s"% (course_type, promo))
                    for sl in self.wdb.slots:
                        avail_course[(course_type, promo)][sl] = 1
                        non_prefered_slot_cost_course[(course_type,
                                                       promo)][sl] = 0
                else:
                    for sl in self.wdb.slots:
                        try:
                            valeur = courses_avail.get(creneau=sl).valeur
                        except:
                            valeur = min(c.valeur for c in courses_avail.filter(creneau=sl))
                        if valeur == 0:
                            avail_course[(course_type, promo)][sl] = 0
                            non_prefered_slot_cost_course[(course_type, promo)][sl] = 5
                        else:
                            avail_course[(course_type, promo)][sl] = 1
                            non_prefered_slot_cost_course[(course_type,
                                                           promo)][sl] \
                                = 1 - float(valeur) / 8

        return non_prefered_slot_cost_course, avail_course

    def add_slot_preferences(self):
        """
         Add the constraints derived from the slot preferences expressed on the database
         """
        print("adding slot preferences")
        # first objective  => minimise use of unpreferred slots for teachers
        # ponderation MIN_UPS_I
        for i in self.wdb.instructors:
            MinNonPreferedSlot(tutor=i,
                               weight=max_weight) \
                .enrich_model(self,
                              ponderation=self.min_ups_i)

        # second objective  => minimise use of unpreferred slots for courses
        # ponderation MIN_UPS_C
        for promo in self.train_prog:
            MinNonPreferedSlot(train_prog=promo,
                               weight=max_weight) \
                .enrich_model(self,
                              ponderation=self.min_ups_c)

    def add_specific_constraints(self):
        """
        Add the active specific constraints stored in the database.
        """
        print("adding active specific constraints")
        for promo in self.train_prog:
            for constr in get_constraints(
                                self.department,
                                week = self.semaine,
                                year = self.an,
                                train_prog = promo, 
                                is_active = True):
                constr.enrich_model(self)

    def update_objective(self):
        for i in self.wdb.instructors:
            self.obj += self.cost_I[i]
        for g in self.wdb.basic_groups:
            self.obj += self.cost_G[g]
        self.set_objective(self.obj)

    def add_TT_constraints(self):
        self.add_stabilization_constraints()

        self.add_core_constraints()

        self.add_rooms_constraints()

        self.add_slot_preferences()

        self.add_dependency_constraints()

        self.add_specific_constraints()

    def add_tt_to_db(self, target_work_copy):
        
        # remove target working copy
        ScheduledCourse.objects \
            .filter(
                cours__module__train_prog__department=self.department,                
                cours__semaine=self.semaine, 
                cours__an=self.an,
                copie_travail=target_work_copy) \
            .delete()
        
        for sl in self.wdb.slots:
            for c in self.wdb.courses:
                if self.get_var_value(self.TT[(sl, c)]) == 1:
                    # No = len(self.wdb.sched_courses \
                    #          .filter(cours__module=c.module,
                    #                  cours__groupe=c.groupe,
                    #                  cours__semaine__lte=self.semaine - 1,
                    #                  copie_travail=0))
                    # No += len(CoursPlace.objects \
                    #           .filter(cours__module=c.module,
                    #                   cours__groupe=c.groupe,
                    #                   cours__semaine=self.semaine,
                    #                   copie_travail=target_work_copy))
                    cp = ScheduledCourse(cours=c,
                                         creneau=sl,
                                         copie_travail=target_work_copy)
                    for rg in c.room_type.members.all():
                        if self.get_var_value(self.TTrooms[(sl, c, rg)]) == 1:
                            cp.room = rg
                    cp.save()
        
        for fc in self.wdb.fixed_courses:
            cp = ScheduledCourse(cours=fc.cours,
                                 creneau=fc.creneau,
                                 room=fc.room,
                                 copie_travail=target_work_copy)
            cp.save()

        # On enregistre les coûts dans la BDD
        TutorCost.objects.filter(
                            department=self.department,
                            semaine=self.wdb.week,
                            an=self.wdb.year).delete()
        GroupFreeHalfDay.objects.filter(
                            groupe__train_prog__department=self.department,
                            semaine=self.wdb.week,
                            an=self.wdb.year).delete()
        GroupCost.objects.filter(
                            groupe__train_prog__department=self.department,
                            semaine=self.wdb.week,
                            an=self.wdb.year).delete()

        for i in self.wdb.instructors:
            cp = TutorCost(
                        department=self.department,
                        tutor=i,
                        an=self.wdb.year, 
                        semaine=self.wdb.week,
                        valeur=self.get_expr_value(self.cost_I[i]))
            cp.save()

        for g in self.wdb.basic_groups:
            djlg = GroupFreeHalfDay(groupe=g,
                                    an=self.wdb.year,
                                    semaine=self.wdb.week,
                                    DJL=self.get_expr_value(self.FHD_G[Time.PM][g]) +
                                        0.5 * self.get_expr_value(
                                        self.FHD_G['AM'][g]))
            djlg.save()
            cg = GroupCost(groupe=g,
                           an=self.wdb.year,
                           semaine=self.wdb.week,
                           valeur=self.get_expr_value(self.cost_G[g]))
            cg.save()


    def optimize(self, time_limit, solver, presolve=2):

        # The solver value shall one of the available 
        # solver corresponding pulp command

        if 'gurobi' in solver.lower():
            # ignore SIGINT while solver is running
            # => SIGINT is still delivered to the solver, which is what we want
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            self.model.solve(GUROBI_CMD(keepFiles=1,
                                        msg=True,
                                        options=[("TimeLimit", time_limit),
                                                 ("Presolve", presolve),
                                                 ("MIPGapAbs", 0.2)]))
        else:
            # TODO Use the solver parameter to get
            # the target class by reflection
            self.model.solve(PULP_CBC_CMD(keepFiles=1,
                                          msg=True,
                                          presolve=presolve,
                                          maxSeconds=time_limit))
        status = self.model.status
        print(LpStatus[status])
        if status == LpStatusOptimal or (not (solver.lower() == 'gurobi') and status == LpStatusNotSolved):
            return self.get_obj_coeffs()

        else:
            print('lpfile has been saved in FlOpTT-pulp.lp')
            return None

    def solve(self, time_limit=3600, target_work_copy=None, solver='gurobi'):
        """
        Generates a schedule from the TTModel
        The solver stops either when the best schedule is obtained or timeLimit
        is reached.

        If stabilize_work_copy is None: does not move the scheduled courses
        whose year group is not in train_prog and fetches from the remote database
        these scheduled courses with work copy 0.

        If target_work_copy is given, stores the resulting schedule under this
        work copy number.
        If target_work_copy is not given, stores under the lowest working copy
        number that is greater than the maximum work copy numbers for the
        considered week.
        Returns the number of the work copy
        """
        print("\nLet's solve week #%g" % self.semaine)


        if target_work_copy is None:
            local_max_wc = ScheduledCourse \
                .objects \
                .filter(
                    cours__module__train_prog__department=self.department,
                    cours__semaine=self.semaine,
                    cours__an=self.an) \
                .aggregate(Max('copie_travail'))['copie_travail__max']

            if local_max_wc is None:
                local_max_wc = -1

            target_work_copy = local_max_wc + 1

        print("Will be stored with work_copy = #%g" % target_work_copy)

        print("Optimization started at", \
            datetime.datetime.today().strftime('%Hh%M'))
        result = self.optimize(time_limit, solver)
        print("Optimization ended at", \
            datetime.datetime.today().strftime('%Hh%M'))

        if result is not None:
            self.add_tt_to_db(target_work_copy)
            reassign_rooms(self.department, self.semaine, self.an, target_work_copy)
            return target_work_copy


def get_constraints(department, week=None, year=None, train_prog=None, is_active=None):
    #
    #  Return constraints corresponding to the specific filters
    #  
    query = Q(department=department)

    if is_active:
        query &= Q(is_active=is_active)

    if week and not year:
        logger.warning(f"Unable to filter constraint for week {week} without specifing year")
        return
        
    if week and train_prog:
        query &= \
            Q(train_prog__abbrev=train_prog) & Q(week__isnull=True) & Q(year__isnull=True) | \
            Q(train_prog__abbrev=train_prog) & Q(week=week) & Q(year=year) | \
            Q(train_prog__isnull=True) & Q(week=week) & Q(year=year) | \
            Q(train_prog__isnull=True) & Q(week__isnull=True) & Q(year__isnull=True)
    elif week:
        query &= Q(week=week) & Q(year=year) | Q(week__isnull=True) & Q(year__isnull=True)            
    elif train_prog:
        query &= Q(train_prog__abbrev=train_prog) | Q(train_prog__isnull=True)

    # Look up the TTConstraint subclasses records to update
    types = TTConstraint.__subclasses__()
    for type in types:
        queryset = type.objects.filter(query)
        
        # Get prefetch  attributes list for the current type
        atributes = type.get_viewmodel_prefetch_attributes()
        if atributes:
            queryset = queryset.prefetch_related(*atributes)
            
        for constraint in queryset.order_by('id'):
            yield constraint
