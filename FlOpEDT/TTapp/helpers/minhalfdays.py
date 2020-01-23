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

from base.models import Time


logger = logging.Logger(__name__)


class MinHalfDaysHelperBase():

    def __init__(self, ttmodel, constraint, ponderation):
        self.ttmodel = ttmodel
        self.constraint = constraint
        self.ponderation = ponderation


    def build_variables(self):
        return None, None, None


    def add_cost(self, cost):
        pass

    
    def add_constraint(self, expression, courses, local_var):
        self.ttmodel.add_constraint(local_var, '==', 1)
        limit = (len(courses) - 1) // 3 + 1

        if self.constraint.weight:
            cost = self.constraint.local_weight() * self.ponderation * (expression - limit * local_var)
            self.add_cost(cost)
        else:
            self.ttmodel.add_constraint(expression, '<=', limit)


    def enrich_model(self, **args):

        expression, courses, local_var = self.build_variables()
        self.add_constraint(expression, courses, local_var)


class MinHalfDaysHelperModule(MinHalfDaysHelperBase):

    def build_variables(self):
        mod_b_h_d = {}
        for d in self.ttmodel.wdb.days:
            
            mod_b_h_d[(self.module, d, Time.AM)] \
                = self.ttmodel.add_var("ModBHD(%s,%s,%s)"
                                    % (self.module, d, Time.AM))
            mod_b_h_d[(self.module, d, Time.PM)] \
                = self.ttmodel.add_var("ModBHD(%s,%s,%s)"
                                    % (self.module, d, Time.PM))
            
            # add constraint linking MBHD to TT
            for apm in [Time.AM, Time.PM]:
                halfdayslots = self.ttmodel.wdb.slots.filter(jour=d,
                                                        heure__apm=apm)
                card = len(halfdayslots)
                expr = self.ttmodel.lin_expr()
                expr += card * mod_b_h_d[(self.module, d, apm)]
                for sl in halfdayslots:
                    for c in self.ttmodel.wdb.courses.filter(module=self.module):
                        expr -= self.ttmodel.TT[(sl, c)]
                self.ttmodel.add_constraint(expr, '>=', 0)
                self.ttmodel.add_constraint(expr, '<=', card - 1)
        
        local_var = self.ttmodel.add_var("MinMBHD_var_%s" % self.module)
        courses = self.ttmodel.wdb.courses.filter(module=self.module)
        expression = self.ttmodel.sum(
            mod_b_h_d[(self.module, d, apm)]
            for d in self.ttmodel.wdb.days
            for apm in [Time.AM, Time.PM])

        return expression, courses, local_var


    def add_cost(self, cost):        
        self.ttmodel.obj += cost


    def enrich_model(self, module=None):
        if module:
            self.module = module
            super().enrich_model()
        else:
            raise("MinHalfDaysHelperModule requires a module argument")


class MinHalfDaysHelperGroup(MinHalfDaysHelperBase):

    def build_variables(self):
        courses = self.ttmodel.wdb.courses.filter(groupe=self.group)

        expression = self.ttmodel.check_and_sum(
            self.ttmodel.GBHD,
            ((self.group, d, apm) for d, apm in self.ttmodel.wdb.slots_by_days))

        local_var = self.ttmodel.add_var("MinGBHD_var_%s" % self.group)

        return expression, courses, local_var


    def add_cost(self, cost):        
        self.ttmodel.add_to_group_cost(self.group, cost)


    def enrich_model(self, group=None):
        if group:
            self.group = group
            super().enrich_model()
        else:
            raise("MinHalfDaysHelperGroup requires a group argument")



class MinHalfDaysHelperTutor(MinHalfDaysHelperBase):

    def build_variables(self):
        courses = self.ttmodel.wdb.courses.filter(tutor=self.tutor)
        expression = self.ttmodel.sum(
            self.ttmodel.IBHD[(self.tutor, d, apm)]
            for d in self.ttmodel.wdb.days
            for apm in [Time.AM, Time.PM])
        local_var = self.ttmodel.add_var("MinIBHD_var_%s" % self.tutor)

        return expression, courses, local_var


    def add_cost(self, cost):        
        self.ttmodel.add_to_inst_cost(self.tutor, cost)


    def add_constraint(self, expression, courses, local_var):
        super().add_constraint(expression, courses, local_var)

        # Try to joincourses
        if self.constraint.join2courses and len(courses) in [2, 4]:
            for d in self.ttmodel.wdb.days:
                sl8h = self.ttmodel.wdb.slots.get(jour=d, heure__no=0)
                sl11h = self.ttmodel.wdb.slots.get(jour=d, heure__no=2)
                sl14h = self.ttmodel.wdb.slots.get(jour=d, heure__no=3)
                sl17h = self.ttmodel.wdb.slots.get(jour=d, heure__no=5)
                for c in courses:
                    for c2 in courses.exclude(id=c.id):
                        if self.constraint.weight:
                            conj_var_AM = self.ttmodel.add_conjunct(self.ttmodel.TT[(sl8h, c)],
                                                               self.ttmodel.TT[(sl11h, c2)])
                            conj_var_PM = self.ttmodel.add_conjunct(self.ttmodel.TT[(sl14h, c)],
                                                               self.ttmodel.TT[(sl17h, c2)])
                            self.ttmodel.add_to_inst_cost(self.tutor,
                                                     self.constraint.local_weight() * self.ponderation * (conj_var_AM + conj_var_PM)/2)
                        else:
                            self.ttmodel.add_constraint(
                                self.ttmodel.TT[(sl8h, c)] + self.ttmodel.TT[(sl11h, c2)],
                                '<=',
                                1)
                            self.ttmodel.add_constraint(
                                self.ttmodel.TT[(sl14h, c)] + self.ttmodel.TT[(sl17h, c2)],
                                '<=',
                                1)        


    def enrich_model(self, tutor=None):
        if tutor:
            self.tutor = tutor
            super().enrich_model()
        else:
            raise("MinHalfDaysHelperTutor requires a tutor argument")            
