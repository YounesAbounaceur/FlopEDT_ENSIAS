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

from django.core.validators import MinValueValidator, MaxValueValidator

from django.db import models

from django.db.models import Q

# from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _

# from caching.base import CachingManager, CachingMixin

from base.models import Time, Department, Module, Group, Slot

from people.models import Tutor

from TTapp.helpers.minhalfdays import MinHalfDaysHelperGroup, MinHalfDaysHelperModule, MinHalfDaysHelperTutor

max_weight = 8


class TTConstraint(models.Model):

    department = models.ForeignKey(Department, null=True, on_delete=models.CASCADE)
    train_prog = models.ForeignKey('base.TrainingProgramme',
                                   null=True,
                                   default=None, 
                                   blank=True, 
                                   on_delete=models.CASCADE)    
    week = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        null=True,
        default=None, 
        blank=True)
    year = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    weight = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(max_weight)],
        null=True, default=None, blank=True)
    comment = models.CharField(max_length=100, null=True, default=None, blank=True)
    is_active = models.BooleanField(verbose_name='Contrainte active?', default=True)

    def local_weight(self):
        return float(self.weight) / max_weight

    class Meta:
        abstract = True

    def enrich_model(self, ttmodel, ponderation=1):
        raise NotImplementedError

    def full_name(self):
        # Return a human readable constraint name
        return str(self)

    def description(self):
        # Return a human readable constraint name
        return self. __doc__ or str(self)

    def get_viewmodel(self):
        #
        # Return a dictionnary with view-related data
        #
        if self.train_prog:
            train_prog_value = f"{self.train_prog.name} ({self.train_prog.abbrev})" 
        else:
            train_prog_value = 'All'
        
        if self.week:
            week_value = f"{self.week} ({self.year})" 
        else:
            week_value = 'All'

        return {
            'model': self.__class__.__name__,
            'pk': self.pk, 
            'is_active': self.is_active,
            'name': self.full_name(),
            'description': self.description(),
            'explanation': self.one_line_description(),
            'comment': self.comment,
            'details': {
                'train_prog': train_prog_value,
                'week': week_value,
                'weight': self.weight,
                }
            }

    def one_line_description(self):
        # Return a human readable constraint name with its attributes
        raise NotImplementedError

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        return ['train_prog', 'department',]


class LimitCourseTypePerPeriod(TTConstraint):  # , pond):
    """
    Bound the number of courses of type 'type' per day/half day
    """
    type = models.ForeignKey('base.CourseType', on_delete=models.CASCADE)
    limit = models.PositiveSmallIntegerField()
    module = models.ForeignKey('base.Module',
                                   null=True,
                                   default=None, 
                                   blank=True,
                                   on_delete=models.CASCADE)
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="Course_type_limits")
    FULL_DAY = 'fd'
    HALF_DAY = 'hd'
    PERIOD_CHOICES = ((FULL_DAY, 'Full day'), (HALF_DAY, 'Half day'))
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES)


    def get_courses_queryset(self, ttmodel, tutor = None):
        """
        Filter courses depending on constraints parameters
        """
        courses_qs = ttmodel.wdb.courses
        courses_filter = {}

        if tutor is not None:
            courses_filter['tutor'] = tutor

        if self.module is not None:
            courses_filter['module'] = self.module

        if self.type is not None:
            courses_filter['type'] = self.type

        if self.train_prog is not None:
            courses_filter['groupe__train_prog'] = self.train_prog

        return courses_qs.filter(**courses_filter)


    def register_expression(self, ttmodel, period_by_day, ponderation, tutor=None):

        courses = self.get_courses_queryset(ttmodel, tutor)

        for day, period in period_by_day:
            expr = ttmodel.lin_expr()
            slots = ttmodel.wdb.slots \
                        .filter(jour=day, heure__apm__contains=period)

            for slot in slots:
                for course in courses:
                    expr += ttmodel.TT[(slot, course)]

            if self.weight is not None:
                var = ttmodel.add_floor(
                                'limit course type per period', 
                                expr,
                                int(self.limit) + 1, 100)
                ttmodel.obj += self.local_weight() * ponderation * var
            else:
                ttmodel.add_constraint(expr, '<=', self.limit)


    def enrich_model(self, ttmodel, ponderation=1.):
        
        if self.period == self.FULL_DAY:
            periods = ['']
        else:
            periods = [Time.AM, Time.PM]

        period_by_day = []
        for day in ttmodel.wdb.days:
            for period in periods:
                period_by_day.append((day, period,))

        try:
            if self.tutors.count():
                for tutor in self.tutors.all():
                    self.register_expression(ttmodel, period_by_day, ponderation, tutor=tutor)
            else:
                self.register_expression(ttmodel, period_by_day, ponderation)
        except ValueError:
            self.register_expression(ttmodel, period_by_day, ponderation)


    def full_name(self):
        return "Limit Course Type Per Period"


    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['module', 'tutors', 'type'])
        return attributes

    def get_viewmodel(self):
        view_model = super().get_viewmodel()

        if self.type:
            type_value = self.type.name
        else:
            type_value = 'All'

        if self.module:
            module_value = self.module.nom
        else:
            module_value = 'All'

        if self.tutors:
            tutor_value = ', '.join([tutor.username for tutor in self.tutors.all()])
        else:
            tutor_value = 'All'

        view_model['details'].update({
            'type': type_value,
            'tutor': tutor_value,
            'module': module_value, })

        return view_model

    def one_line_description(self):
        text = "Pas plus de " + str(self.limit) + ' ' + str(self.type)
        if self.module:
            text += " de " + self.module.nom
        text += " par "
        if self.period == self.FULL_DAY:
            text += 'jour'
        else:
            text += 'demi-journée'
        if self.tutors.exists():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.train_prog:
            text += ' en ' + str(self.train_prog)

        return text


class ReasonableDays(TTConstraint):
    """
    Allow to limit long days (with the first and last slot of a day). For a
    given parameter,
    a None value builds the constraint for all possible values,
    e.g. promo = None => the constraint holds for all promos.
    """
    groups = models.ManyToManyField('base.Group',
                                    blank=True,
                                    related_name="reasonable_day_constraints")
    tutors = models.ManyToManyField('people.Tutor',
                                    blank=True,
                                    related_name="reasonable_day_constraints")


    def get_courses_queryset(self, ttmodel, tutor=None, group=None):
        """
        Filter courses depending on constraints parameters
        """
        courses_qs = ttmodel.wdb.courses
        courses_filter = {}

        if tutor is not None:
            courses_filter['tutor'] = tutor

        if group is not None:
            courses_filter['groupe'] = group

        if self.train_prog is not None:
            courses_filter['groupe__train_prog'] = self.train_prog

        return courses_qs.filter(**courses_filter)


    def update_combinations(self, ttmodel, slot_boundaries, combinations, tutor=None, group=None):
        """
        Update courses combinations for slot boundaries with all courses 
        corresponding to the given filters (tutors, groups)
        """
        courses_query = self.get_courses_queryset(ttmodel, tutor=tutor, group=group)
        courses_set = set(courses_query)
        
        for first_slot, last_slot in slot_boundaries:
            while courses_set:
                c1 = courses_set.pop()
                for c2 in courses_set:
                    combinations.add(((first_slot, c1), (last_slot, c2),))


    def register_expression(self, ttmodel, ponderation, combinations):
        """
        Update model with expressions corresponding to 
        all courses combinations
        """
        for first, last in combinations:
            if self.weight is not None:
                conj_var = ttmodel.add_conjunct(ttmodel.TT[first], ttmodel.TT[last])
                ttmodel.obj += self.local_weight() * ponderation * conj_var
            else:
                ttmodel.add_constraint(ttmodel.TT[first] + ttmodel.TT[last], '<=', 1)


    def enrich_model(self, ttmodel, ponderation=1):

        # Using a set type ensure that all combinations are 
        # unique throw tutor and group filters
        combinations = set()

        # Get a dict with the first and last slot by day
        slots = Slot.objects \
                    .filter(heure__no__in=[0,5,]) \
                    .order_by('heure__no') 
        
        slot_boundaries = {}
        for slot in slots: 
            slot_boundaries.setdefault(slot.jour, []).append(slot)
              
        # Create all combinations with slot boundaries for all courses 
        # corresponding to the given filters (tutors, groups)
        try:
            if self.tutors.count():
                for tutor in self.tutors.all():
                    self.update_combinations(ttmodel, slot_boundaries.values(), combinations, tutor=tutor)
            elif self.groups.count():
                for group in self.groups.all():
                    self.update_combinations(ttmodel, slot_boundaries.values(), combinations, group=group)
            else:
                self.update_combinations(ttmodel, slot_boundaries.values(), combinations)
        except ValueError:
            self.update_combinations(ttmodel, slot_boundaries.values(), combinations)

        self.register_expression(ttmodel, ponderation, combinations)


    def one_line_description(self):
        text = "Des journées pas trop longues"
        if self.tutors.count():
            text += ' pour ' + ', '.join([tutor.username for tutor in self.tutors.all()])
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.groups.count():
            text += ' avec les groupes ' + ', '.join([group for group in self.groups.all()])
        return text


    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['groups', 'tutors'])
        return attributes


class Stabilize(TTConstraint):
    """
    Allow to realy stabilize the courses of a category
    If general is true, none of the other (except week and work_copy) is
    relevant.
    --> In this case, each course c placed:
        - in a unused slot costs 1,
        - in a unused half day (for tutor and/or group) cost ponderation
    If general is False, it Fixes train_prog/tutor/group courses (or tries to if
    self.weight)
    """
    general = models.BooleanField(
        verbose_name='Stabiliser tout?',
        default=False)

    group = models.ForeignKey('base.Group', null=True, default=None, on_delete=models.CASCADE)
    module = models.ForeignKey('base.Module', null=True, default=None, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType', null=True, default=None, on_delete=models.CASCADE)
    work_copy = models.PositiveSmallIntegerField(default=0)
    fixed_days = models.ManyToManyField('base.Day',
                                        related_name='days_to_fix',
                                        blank=True)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'module', 'tutor', 'type'])
        return attributes

    def enrich_model(self, ttmodel, ponderation=1):
        sched_courses = ttmodel.wdb.sched_courses.filter(copie_travail=self.work_copy)
        for day in self.fixed_days.all():
            for sc in sched_courses.filter(creneau__jour=day):
                ttmodel.add_constraint(ttmodel.TT[(sc.creneau, sc.cours)], '==', 1)
            for sc in sched_courses.exclude(creneau__jour=day):
                for sl in ttmodel.wdb.slots.filter(jour=day):
                    ttmodel.add_constraint(ttmodel.TT[(sl, sc.cours)], '==', 0)

        if self.general:
            # nb_changements_I=dict(zip(ttmodel.wdb.instructors,[0 for i in ttmodel.wdb.instructors]))
            for sl in ttmodel.wdb.slots:
                for c in ttmodel.wdb.courses:
                    if not sched_courses.filter(cours__tutor=c.tutor,
                                                creneau=sl,
                                                ):
                        ttmodel.obj += ttmodel.TT[(sl, c)]
                        # nb_changements_I[c.tutor]+=ttmodel.TT[(sl,c)]
                    if not sched_courses.filter(cours__tutor=c.tutor,
                                                creneau__jour=sl.jour,
                                                creneau__heure__apm=sl.heure.apm):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]
                        # nb_changements_I[i]+=ttmodel.TT[(sl,c)]
                    if not sched_courses.filter(cours__groupe=c.groupe,
                                                creneau__jour=sl.jour,
                                                creneau__heure__apm=sl.heure.apm):
                        ttmodel.obj += ponderation * ttmodel.TT[(sl, c)]

        else:
            fc = ttmodel.wdb.courses
            if self.tutor is not None:
                fc = fc.filter(tutor=self.tutor)
            if self.type is not None:
                fc = fc.filter(type=self.type)
            if self.train_prog is not None:
                fc = fc.filter(groupe__train_prog=self.train_prog)
            if self.group:
                fc = fc.filter(groupe=self.group)
            if self.module:
                fc = fc.filter(module=self.module)
            for c in fc:
                sched_c = ttmodel.wdb \
                    .sched_courses \
                    .get(cours=c,
                         copie_travail=self.work_copy)
                chosen_slot = sched_c.creneau
                chosen_roomgroup = sched_c.room
                if self.weight is not None:
                    ttmodel.obj -= self.local_weight() \
                                   * ponderation * ttmodel.TT[(chosen_slot, c)]

                else:
                    ttmodel.add_constraint(ttmodel.TT[(chosen_slot, c)],
                                           '==',
                                           1)
                    if c.room_type in chosen_roomgroup.types.all():
                        ttmodel.add_constraint(
                            ttmodel.TTrooms[(chosen_slot, c, chosen_roomgroup)],
                            '==',
                            1)

    def one_line_description(self):
        text = "Minimiser les changements"
        if self.type:
            text += " pour les " + str(self.type)
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.group:
            text += ' du groupe ' + str(self.group)
        text += ': copie ' + str(self.work_copy)
        return text


class MinHalfDays(TTConstraint):
    """
    All courses will fit in a minimum of half days
    You have to chose EITHER tutor OR group OR module
    Optional for tutors : if 2 courses only, possibility to join it
    """
    groups = models.ManyToManyField('base.Group', blank=True)
    tutors = models.ManyToManyField('people.Tutor', blank=True)
    modules = models.ManyToManyField('base.Module', blank=True)

    join2courses = models.BooleanField(
        verbose_name='If a tutor has 2 or 4 courses only, join it?',
        default=False)


    def enrich_model(self, ttmodel, ponderation=1):

        if self.tutors.exists():
            helper = MinHalfDaysHelperTutor(ttmodel, self, ponderation)
            for tutor in self.tutors.all():
                helper.enrich_model(tutor=tutor)

        elif self.modules.exists():
            helper = MinHalfDaysHelperModule(ttmodel, self, ponderation)
            for module in self.modules.all():
                helper.enrich_model(module=module)

        elif self.groups.exists():
            helper = MinHalfDaysHelperGroup(ttmodel, self, ponderation)
            for group in self.groups.all():
                helper.enrich_model(group=group)
                
        else:
            print("MinHalfDays must have at least one tutor or one group or one module --> Ignored")
            return


    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model['details']

        if self.tutors.exists():
            details.update({'tutors': ', '.join([tutor.username for tutor in self.tutors.all()])})

        if self.groups.exists():
            details.update({'groups': ', '.join([group.nom for group in self.groups.all()])})

        if self.modules.exists():
            details.update({'modules': ', '.join([module.nom for module in self.modules.all()])})

        return view_model
        

    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.tutors.exists():
            text += ' de : ' + ', '.join([tutor.username for tutor in self.tutors.all()])

        if self.groups.exists():
            text += ' du(des) groupe(s) : ' + ', '.join([group.nom for group in self.groups.all()])

        if self.modules.exists():
            text += ' de : ' + ', '.join([str(module) for module in self.modules.all()])
            
        if self.train_prog:
            text += ' en ' + str(self.train_prog)

        return text
        

class MinNonPreferedSlot(TTConstraint):
    """
    Minimize the use of unprefered Slots
    NB: You HAVE TO chose either tutor OR train_prog
    """
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['tutor'])
        return attributes                              

    # is not called when save() is
    def clean(self):
        if not self.tutor and not self.train_prog:
            raise ValidationError({
                'train_prog': ValidationError(_('Si pas de prof alors promo.',
                                                code='invalid')),
                'tutor': ValidationError(_('Si pas de promo alors prof.',
                                           code='invalid'))})

    def enrich_model(self, ttmodel, ponderation=1):
        if self.tutor is not None:
            filtered_courses = ttmodel.wdb.courses \
                .filter(tutor=self.tutor)
        else:
            filtered_courses = ttmodel.wdb.courses \
                .filter(groupe__train_prog=self.train_prog)
            # On exclut les cours de sport!
            filtered_courses = \
                filtered_courses.exclude(module__abbrev='SC')
        basic_groups = ttmodel.wdb.basic_groups \
            .filter(train_prog=self.train_prog)
        for sl in ttmodel.wdb.slots:
            for c in filtered_courses:
                if self.tutor is not None:
                    cost = (float(self.weight) / max_weight) \
                           * ponderation * ttmodel.TT[(sl, c)] \
                           * ttmodel.unp_slot_cost[c.tutor][sl]
                    ttmodel.add_to_slot_cost(sl, cost)
                    ttmodel.add_to_inst_cost(c.tutor, cost)
                else:
                    for g in basic_groups:
                        if c.groupe in ttmodel.wdb.basic_groups_surgroups[g]:
                            cost = self.local_weight() \
                                   * ponderation * ttmodel.TT[(sl, c)] \
                                   * ttmodel.unp_slot_cost_course[c.type,
                                                                  self.train_prog][sl]
                            ttmodel.add_to_group_cost(g, cost)
                            ttmodel.add_to_slot_cost(sl, cost)

    def one_line_description(self):
        text = "Respecte les préférences"
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_prog:
            text += ' des groupes de ' + str(self.train_prog)
        return text


class AvoidBothSlots(TTConstraint):
    """
    Avoid the use of two slots
    Idéalement, on pourrait paramétrer slot1, et slot2 à partir de slot1... Genre slot1
    c'est 8h n'importe quel jour, et slot2 14h le même jour...
    """
    slot1 = models.ForeignKey('base.Slot', related_name='slot1', on_delete=models.CASCADE)
    slot2 = models.ForeignKey('base.Slot', related_name='slot2', on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group', null=True, on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['group', 'tutor'])
        return attributes                              

    def enrich_model(self, ttmodel, ponderation=1):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.train_prog is not None:
            fc = fc.filter(groupe__train_prog=self.train_prog)
        if self.group:
            fc = fc.filter(groupe=self.group)
        for c1 in fc:
            for c2 in fc.exclude(id__lte=c1.id):
                if self.weight is not None:
                    conj_var = ttmodel.add_conjunct(
                        ttmodel.TT[(self.slot1, c1)],
                        ttmodel.TT[(self.slot2, c2)])
                    ttmodel.obj += self.local_weight() * ponderation * conj_var
                else:
                    ttmodel.add_constraint(ttmodel.TT[(self.slot1, c1)]
                                           + ttmodel.TT[(self.slot2, c2)],
                                           '<=',
                                           1)

    def one_line_description(self):
        text = "Pas à la fois " + str(self.slot1) + " et " + str(self.slot2)
        if self.tutor:
            text += ' pour ' + str(self.tutor)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        return text

# ========================================
# The following constraints have to be checked!!!
# ========================================

# class AvoidIsolatedSlot(TTConstraint):
#     """
#     Avoid the use of an isolated slot
#     RESTE A FAIRE (est-ce possible en non quadratique?)
#     """
#     train_prog = models.ForeignKey('base.TrainingProgramme',
#                                    null = True,
#                                    default = None,
#                                    on_delete=models.CASCADE)
#     group = models.ForeignKey('base.Groupe', null=True, on_delete=models.CASCADE)
#     tutor = models.ForeignKey('people.Tutor', null=True, on_delete=models.CASCADE)
#
#     def enrich_model(self, ttmodel, ponderation=1):
#         fc = ttmodel.wdb.courses
#         if self.tutor is not None:
#             fc = fc.filter(tutor = self.tutor)
#         if self.train_prog:
#             fc = fc.filter(groupe__train_prog = self.promo)
#         if self.group:
#             fc = fc.filter(groupe=self.group)


class SimultaneousCourses(TTConstraint):
    """
    Force two courses to be simultaneous
    It modifies the core constraints that impides such a simultaneity
    """
    course1 = models.ForeignKey('base.Course', related_name='course1', on_delete=models.CASCADE)
    course2 = models.ForeignKey('base.Course', related_name='course2', on_delete=models.CASCADE)

    @classmethod
    def get_viewmodel_prefetch_attributes(cls):
        attributes = super().get_viewmodel_prefetch_attributes()
        attributes.extend(['course1', 'course2'])
        return attributes

    def enrich_model(self, ttmodel, ponderation=1):
        same_tutor = (self.course1.tutor == self.course2.tutor)
        for sl in ttmodel.wdb.slots:
            var1 = ttmodel.TT[(sl, self.course1)]
            var2 = ttmodel.TT[(sl, self.course2)]
            ttmodel.add_constraint(var1 - var2, '==', 0)
            # A compléter, l'idée est que si les cours ont le même prof, ou des
            # groupes qui se superposent, il faut veiller à supprimer les core
            # constraints qui empêchent que les cours soient simultanés...
            if same_tutor:
                name_tutor_constr = str('core_tutor_'
                                        + str(self.course1.tutor)
                                        + '_'
                                        + str(sl))
                tutor_constr = ttmodel.get_constraint(name_tutor_constr)
                print(tutor_constr)
                if (ttmodel.var_coeff(var1, tutor_constr), ttmodel.var_coeff(var2, tutor_constr)) == (1, 1):
                    ttmodel.change_var_coeff(var2, tutor_constr, 0)
            for bg in ttmodel.wdb.basic_groups:
                bg_groups = ttmodel.wdb.basic_groups_surgroups[bg]
                if self.course1.groupe in bg_groups and self.course2.groupe in bg_groups:
                    name_group_constr = 'core_group_' + str(bg) + '_' + str(sl)
                    group_constr = ttmodel.get_constraint(name_group_constr)
                    if (ttmodel.var_coeff(var1, group_constr), ttmodel.var_coeff(var2, group_constr)) == (1, 1):
                        ttmodel.change_var_coeff(var2, group_constr, 0)

    def one_line_description(self):
        text = "Les cours " + str(self.course1) + " et " + str(self.course2) + " doivent être simultanés !"

class LimitedSlotChoices(TTConstraint):
    """
    Limit the possible slots for the cources
    """
    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    possible_slots = models.ManyToManyField('base.Slot',
                                            related_name="limited_courses")

    def enrich_model(self, ttmodel, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.train_prog is not None:
            fc = fc.filter(groupe__train_prog=self.train_prog)
        if self.group is not None:
            fc = fc.filter(groupe=self.group)
        possible_slots_ids = self.possible_slots.values_list('id', flat=True)

        for c in fc:
            for sl in ttmodel.wdb.slots.exclude(id__in = possible_slots_ids):
                if self.weight is not None:
                    ttmodel.obj += self.local_weight() * ponderation * ttmodel.TT[(sl, c)]
                else:
                    ttmodel.add_constraint(ttmodel.TT[(sl, c)], '==', 0)

    def one_line_description(self):
        text = "Les "
        if self.type:
            text += str(self.type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'à "
        for sl in self.possible_slots.values_list():
            text += str(sl) + ', '
        return text


class LimitedRoomChoices(TTConstraint):
    """
    Limit the possible rooms for the cources
    """
    module = models.ForeignKey('base.Module',
                               null=True,
                               default=None,
                               on_delete=models.CASCADE)
    tutor = models.ForeignKey('people.Tutor',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    group = models.ForeignKey('base.Group',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    type = models.ForeignKey('base.CourseType',
                              null=True,
                              default=None,
                              on_delete=models.CASCADE)
    possible_rooms = models.ManyToManyField('base.RoomGroup',
                                            related_name="limited_rooms")

    def enrich_model(self, ttmodel, ponderation=1.):
        fc = ttmodel.wdb.courses
        if self.tutor is not None:
            fc = fc.filter(tutor=self.tutor)
        if self.module is not None:
            fc = fc.filter(module=self.module)
        if self.type is not None:
            fc = fc.filter(type=self.type)
        if self.group is not None:
            fc = fc.filter(groupe=self.group)
        possible_rooms_ids = self.possible_rooms.values_list('id', flat=True)

        for c in fc:
            for sl in ttmodel.wdb.slots:
                for rg in ttmodel.wdb.room_groups.filter(types__in=[c.room_type]).exclude(id__in = possible_rooms_ids):
                    if self.weight is not None:
                        ttmodel.obj += self.local_weight() * ponderation * ttmodel.TTrooms[(sl, c, rg)]
                    else:
                        ttmodel.add_constraint(ttmodel.TTrooms[(sl, c,rg)], '==', 0)

    def one_line_description(self):
        text = "Les "
        if self.type:
            text += str(self.type)
        else:
            text += "cours"
        if self.module:
            text += " de " + str(self.module)
        if self.tutor:
            text += ' de ' + str(self.tutor)
        if self.train_prog:
            text += ' en ' + str(self.train_prog)
        if self.group:
            text += ' avec le groupe ' + str(self.group)
        text += " ne peuvent avoir lieu qu'en salle "
        for sl in self.possible_rooms.values_list():
            text += str(sl) + ', '
        return text
