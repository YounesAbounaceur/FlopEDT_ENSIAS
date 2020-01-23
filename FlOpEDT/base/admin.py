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
from django.contrib import admin
from django.db.models.fields.related import RelatedField

from people.models import Tutor, User

from base.models import Day, RoomGroup, Module, Course, Group, Slot, \
    UserPreference, Time, ScheduledCourse, EdtVersion, CourseModification, \
    PlanningModification, BreakingNews, TrainingProgramme, ModuleDisplay, \
    Regen, Holiday, TrainingHalfDay, RoomPreference, RoomSort, \
    CoursePreference, Dependency, RoomType, Department, CourseType

from core.department import get_model_department_lookup

import django.contrib.auth as auth
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import related as related_fields

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, DropdownFilterSimple

logger = logging.getLogger('admin')

# from core.models import Book

# class ProfResource(resources.ModelResource):
#
#    class Meta:
#        model = Prof
#        # fields = ('abbrev',)

# <editor-fold desc="RESOURCES">
# -----------------
# -- PREFERENCES --
# -----------------


class CoursPlaceResource(resources.ModelResource):
    id = fields.Field(column_name='id_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Course, 'id'))
    no = fields.Field(column_name='num_cours',
                      attribute='cours',
                      widget=ForeignKeyWidget(Course, 'no'))
    prof = fields.Field(column_name='prof_nom',
                        attribute='cours__tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    # prof_first_name = fields.Field(column_name='prof_first_name',
    #                                attribute='cours__tutor',
    #                                widget=ForeignKeyWidget(Tutor,
    #                                 'first_name'))
    # prof_last_name = fields.Field(column_name='prof_last_name',
    #                               attribute='cours__tutor',
    #                               widget=ForeignKeyWidget(Tutor, 'last_name'))
    groupe = fields.Field(column_name='gpe_nom',
                          attribute='cours__groupe',
                          widget=ForeignKeyWidget(Group, 'nom'))
    promo = fields.Field(column_name='gpe_promo',
                         attribute='cours__groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    module = fields.Field(column_name='module',
                          attribute='cours__module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    jour = fields.Field(column_name='jour',
                        attribute='creneau__jour',
                        widget=ForeignKeyWidget(Day, 'no'))
    heure = fields.Field(column_name='heure',
                         attribute='creneau__heure',
                         widget=ForeignKeyWidget(Time, 'no'))
    # salle = fields.Field(column_name = 'salle',
    #                      attribute = 'salle',
    #                      widget = ForeignKeyWidget(Salle,'nom'))
    room = fields.Field(column_name='room',
                        attribute='room',
                        widget=ForeignKeyWidget(RoomGroup, 'name'))
    room_type = fields.Field(column_name='room_type',
                             attribute='cours__room_type',
                             widget=ForeignKeyWidget(RoomType, 'name'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='cours__module__display',
                            widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='cours__module__display',
                             widget=ForeignKeyWidget(ModuleDisplay, 'color_txt'))

    class Meta:
        model = ScheduledCourse
        fields = ('id', 'no', 'groupe', 'promo', 'color_bg', 'color_txt',
                  'module', 'jour', 'heure', 'semaine', 'room', 'prof',
                  'room_type')


class CoursResource(resources.ModelResource):
    promo = fields.Field(column_name='promo',
                         attribute='groupe__train_prog',
                         widget=ForeignKeyWidget(TrainingProgramme, 'abbrev'))
    prof = fields.Field(column_name='prof',
                        attribute='tutor',
                        widget=ForeignKeyWidget(Tutor, 'username'))
    module = fields.Field(column_name='module',
                          attribute='module',
                          widget=ForeignKeyWidget(Module, 'abbrev'))
    groupe = fields.Field(column_name='groupe',
                          attribute='groupe',
                          widget=ForeignKeyWidget(Group, 'nom'))
    color_bg = fields.Field(column_name='color_bg',
                            attribute='module__display',
                            widget=ForeignKeyWidget(ModuleDisplay, 'color_bg'))
    color_txt = fields.Field(column_name='color_txt',
                             attribute='module__display',
                             widget=ForeignKeyWidget(ModuleDisplay, 'color_txt'))
    room_type = fields.Field(column_name='room_type',
                             attribute='room_type',
                             widget=ForeignKeyWidget(RoomType, 'name'))

    class Meta:
        model = Course
        fields = ('id', 'no', 'tutor_name', 'groupe', 'promo', 'module',
                  'color_bg', 'color_txt', 'prof', 'room_type')


class SemaineAnResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ("semaine", "an")


class DispoResource(resources.ModelResource):
    prof = fields.Field(attribute='user',
                        widget=ForeignKeyWidget(User, 'username'))
    jour = fields.Field(attribute='creneau__jour',
                        widget=ForeignKeyWidget(Day, 'no'))
    heure = fields.Field(attribute='creneau__heure',
                         widget=ForeignKeyWidget(Time, 'no'))

    class Meta:
        model = UserPreference
        fields = ('jour', 'heure', 'valeur', 'prof')


class UnavailableRoomsResource(resources.ModelResource):
    day = fields.Field(column_name='jour',
                        attribute='creneau__jour',
                        widget=ForeignKeyWidget(Day, 'no'))
    slot = fields.Field(column_name='heure',
                         attribute='creneau__heure',
                         widget=ForeignKeyWidget(Time, 'no'))
    
    class Meta:
        model = RoomPreference
        fields = ("room", "day", "slot")


class BreakingNewsResource(resources.ModelResource):
    class Meta:
        model = BreakingNews
        fields = ("id", "x_beg", "x_end", "y", "txt", "fill_color", "strk_color", "is_linked")

class VersionResource(resources.ModelResource):
    class Meta:
        model = EdtVersion;
        fields = ("an", "semaine", "version")



# </editor-fold desc="RESOURCES">



        
# <editor-fold desc="ADMIN_MENU">
# ----------------
# -- ADMIN MENU --
# ----------------

class DepartmentModelAdmin(admin.ModelAdmin):
    #
    # Support filter and udpate of department specific related items
    #
    department_field_name = 'department'
    department_field_tuple = (department_field_name,)

    def get_exclude(self, request, obj=None):
        # Hide department field if a department attribute exists 
        # on the related model and a department value has been set
        base = super().get_exclude(request, obj)
        exclude = list() if base is None else base

        if hasattr(request, 'department'):
            for field in self.model._meta.get_fields():
                if not field.auto_created and field.related_model == Department:
                    exclude.append(field.name)

        return exclude

    
    def save_model(self, request, obj, form, change):
        #
        # Set department field value if exists on the model
        #
        if hasattr(request, 'department'):
            for field in self.model._meta.get_fields():
                if not field.auto_created and field.related_model == Department:
                    if isinstance(field, related_fields.ForeignKey):
                        setattr(obj, field.name, request.department)
        
        super().save_model(request, obj, form, change)        

    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        model = form.instance
        if hasattr(request, 'department') and not change:
            for field in model._meta.get_fields():
                if field.related_model == Department:
                    if isinstance(field, related_fields.ManyToManyField):
                        field.save_form_data(model, [request.department,])


    def get_department_lookup(self, department):
        """
        Hook for overriding default department lookup research
        """
        return get_model_department_lookup(self.model, department)

    
    def get_queryset(self, request):
        """
        Filter only department related instances
        """
        qs = super().get_queryset(request)
        
        try:
            if hasattr(request, 'department'):
                related_filter = self.get_department_lookup(request.department)
                if related_filter:                    
                    return qs.filter(**related_filter).distinct()
        except FieldDoesNotExist:
            pass

        return qs


    def formfield_with_department_filtering(self, db_field, request, kwargs):
        """
        Filter form fields for with specific department related items
        """

        if hasattr(request, 'department') and db_field.related_model: 
            related_filter = get_model_department_lookup(db_field.related_model, request.department)
            if related_filter:
                db = kwargs.get('using')
                queryset = self.get_field_queryset(db, db_field, request)
                if queryset:
                    kwargs["queryset"] = queryset


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        self.formfield_with_department_filtering(db_field, request, kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     self.formfield_with_department_filtering(db_field, request, kwargs)
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)


    def get_field_queryset(self, db, db_field, request):

        queryset = super().get_field_queryset(db, db_field, request)
        related_filter = get_model_department_lookup(db_field.related_model, request.department)

        if related_filter:
            if queryset:
                return queryset.filter(**related_filter).distinct()
            else:
                return db_field.remote_field \
                        .model._default_manager \
                        .using(db) \
                        .filter(**related_filter).distinct()

        return queryset


class BreakingNewsAdmin(DepartmentModelAdmin):
    list_display = ('week', 'year', 'x_beg', 'x_end', 'y', 'txt',
                    'fill_color', 'strk_color')
    ordering = ('-year', '-week')

    
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('day', 'week', 'year')
    ordering = ('-year', '-week', 'day')
    list_filter = (
        ('day', DropdownFilterSimple),
        ('year', DropdownFilterAll),
        ('week', DropdownFilterAll),
    )


class TrainingHalfDayAdmin(DepartmentModelAdmin):
    list_display = ('train_prog', 'day', 'week', 'year', 'apm')
    ordering = ('-year', '-week', 'train_prog', 'day')
    

class GroupAdmin(DepartmentModelAdmin):
    list_display = ('nom', 'type', 'size', 'train_prog')
    filter_horizontal = ('parent_groups',)
    ordering = ('size',)
    list_filter = (('train_prog', DropdownFilterRel),
                   )

class RoomGroupAdmin(DepartmentModelAdmin):
    list_display = ('name',)

  
class RoomPreferenceAdmin(DepartmentModelAdmin):
    list_display = ('room', 'semaine', 'an', 'creneau', 'valeur')
    ordering = ('-an','-semaine','creneau')
    list_filter = (
        ('room', DropdownFilterRel),
        ('an', DropdownFilterAll),
        ('semaine', DropdownFilterAll),
    )

    
class RoomSortAdmin(DepartmentModelAdmin):
    list_display = ('for_type', 'prefer', 'unprefer',)
    list_filter = (
        ('for_type', DropdownFilterRel),
        ('prefer', DropdownFilterRel),
        ('unprefer', DropdownFilterRel),
    )

    
class ModuleAdmin(DepartmentModelAdmin):
    list_display = ('nom', 'ppn', 'abbrev',
                    'head',
                    'train_prog')
    ordering = ('abbrev',)
    list_filter = (
        ('head', DropdownFilterRel),
        ('train_prog', DropdownFilterRel),)

class CourseAdmin(DepartmentModelAdmin):
    list_display = ('module', 'type', 'groupe', 'tutor', 'semaine', 'an')
    ordering = ('an', 'semaine', 'module', 'type', 'no', 'groupe', 'tutor')
    list_filter = (
        ('tutor', DropdownFilterRel),
        ('an', DropdownFilterAll),
        ('semaine', DropdownFilterAll),
        ('type', DropdownFilterRel),
        ('groupe', DropdownFilterRel),
    )


class CoursPlaceAdmin(DepartmentModelAdmin):

    def cours_semaine(o):
        return str(o.cours.semaine)

    cours_semaine.short_description = 'Semaine'
    cours_semaine.admin_order_field = 'cours__semaine'

    def cours_an(o):
        return str(o.cours.an)

    cours_an.short_description = 'Année'
    cours_an.admin_order_field = 'cours__an'

    list_display = (cours_semaine, cours_an, 'cours', 'creneau', 'room')
    ordering = ('creneau', 'cours', 'room')
    list_filter = (
        ('cours__tutor', DropdownFilterRel),
        ('cours__an', DropdownFilterAll),
        ('cours__semaine', DropdownFilterAll),)


class CoursePreferenceAdmin(DepartmentModelAdmin):
    list_display = ('course_type', 'train_prog', 'creneau',
                    'valeur', 'semaine', 'an')
    ordering = ('-an', '-semaine')
    list_filter = (('semaine', DropdownFilterAll),
                   ('an', DropdownFilterAll),
                   ('train_prog', DropdownFilterRel),
                   )
    

class DependencyAdmin(DepartmentModelAdmin):
    def cours1_semaine(o):
        return str(o.cours.semaine)

    cours1_semaine.short_description = 'Semaine'
    cours1_semaine.admin_order_field = 'cours1__semaine'

    def cours1_an(o):
        return str(o.cours.an)

    cours1_an.short_description = 'Année'
    cours1_an.admin_order_field = 'cours1__an'

    list_display = ('cours1', 'cours2', 'successifs', 'ND')
    list_filter = (('cours1__an', DropdownFilterAll),
                   ('cours1__semaine', DropdownFilterAll),
                   )

    
class CourseModificationAdmin(DepartmentModelAdmin):
    def cours_semaine(o):
        return str(o.cours.semaine)

    cours_semaine.short_description = 'Semaine'
    cours_semaine.admin_order_field = 'cours__semaine'

    def cours_an(o):
        return str(o.cours.an)

    cours_an.short_description = 'Année'
    cours_an.admin_order_field = 'cours__an'

    list_display = ('cours', cours_semaine, cours_an,
                    'version_old', 'room_old', 'creneau_old',
                    'updated_at', 'initiator'
                    )
    list_filter = (('initiator', DropdownFilterRel),
                   ('cours__an', DropdownFilterAll),
                   ('cours__semaine', DropdownFilterAll),)
    ordering = ('-updated_at', 'an_old', 'semaine_old')


class PlanningModificationAdmin(DepartmentModelAdmin):
    list_display = ('cours', 'semaine_old', 'an_old',
                    'tutor_old',
                    'updated_at',
                    'initiator'
                    )
    ordering = ('-updated_at', 'an_old', 'semaine_old')
    list_filter = (('initiator', DropdownFilterRel),
                   ('semaine_old', DropdownFilterAll),
                   ('an_old', DropdownFilterAll),)


class DispoAdmin(DepartmentModelAdmin):
    list_display = ('user', 'creneau', 'valeur', 'semaine', 'an')
    ordering = ('user', 'an', 'semaine', 'creneau', 'valeur')
    list_filter = (('creneau', DropdownFilterRel),
                   ('semaine', DropdownFilterAll),
                   ('user', DropdownFilterRel),
                   )


class RegenAdmin(DepartmentModelAdmin):
    list_display = ('an', 'semaine', 'full', 'fday', 'fmonth', 'fyear', 'stabilize', 'sday', 'smonth', 'syear', )
    ordering = ('-an', '-semaine')


# </editor-fold desc="ADMIN_MENU">




# admin.site.unregister(auth.models.User)
admin.site.unregister(auth.models.Group)

admin.site.register(Holiday, HolidayAdmin)
admin.site.register(TrainingHalfDay, TrainingHalfDayAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(RoomGroup, RoomGroupAdmin)
admin.site.register(RoomPreference, RoomPreferenceAdmin)
admin.site.register(RoomSort, RoomSortAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseModification, CourseModificationAdmin)
admin.site.register(CoursePreference, CoursePreferenceAdmin)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(PlanningModification, PlanningModificationAdmin)
admin.site.register(ScheduledCourse, CoursPlaceAdmin)
admin.site.register(UserPreference, DispoAdmin)
admin.site.register(BreakingNews, BreakingNewsAdmin)
admin.site.register(Regen,RegenAdmin)
