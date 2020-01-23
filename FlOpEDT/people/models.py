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



from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import Department

# Create your models here.


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    rights = models.PositiveSmallIntegerField(verbose_name="Droits particuliers",
                                              default=0)
    # 0b azmyx en binaire
    # x==1 <=> quand "modifier Cours" coché, les cours sont colorés
    #          avec la dispo du prof
    # y==1 <=> je peux changer les dispos de tout le monde
    # m==1 <=> je peux modifier l'emploi du temps comme bon me semble
    # FUTUR
    # z==1 <=> je peux changer les dispos des vacataires d'un module dont
    #          je suis responsable
    # a==1 <=> je peux surpasser les contraintes lors de la modification
    #          de cours

    def uni_extended(self):
        ret = self.username + '<'
        if self.is_student:
            ret += 'S'
        if self.is_tutor:
            ret += 'T'
        ret += '>'
        ret += '(' + str(self.rights) + ')'
        return ret

    class Meta:
       ordering = ['username',]        
        

class Tutor(User):
    FULL_STAFF = 'fs'
    SUPP_STAFF = 'ss'
    BIATOS = 'bi'
    TUTOR_CHOICES = ((FULL_STAFF, "Full staff"),
                     (SUPP_STAFF, "Supply staff"),
                     (BIATOS, "BIATOS"))
    status = models.CharField(max_length=2,
                              choices=TUTOR_CHOICES,
                              verbose_name="Status",
                              default=FULL_STAFF)
    pref_slots_per_day = models.PositiveSmallIntegerField(
        verbose_name="How many slots per day would you prefer ?",
        default=4)
    departments =  models.ManyToManyField(Department, blank=True)   

    def uni_extended(self):
        ret = super(Tutor,self).uni_extended()
        ret += '-' + self.status + '-' + 'S' + str(self.pref_slots_per_day)
        return ret


class FullStaff(Tutor):
    # deprected since multi departements insertion
    department = models.CharField(max_length=50, default='INFO', null=True, blank=True)
    is_iut = models.BooleanField(default=True)

    def uni_extended(self):
        ret = super(FullStaff,self).uni_extended()
        ret += '-D' + self.department + '-'
        if not self.is_iut:
            ret += 'n'
        ret += 'IUT'
        return ret

    class Meta:
        verbose_name = 'FullStaff' 


class SupplyStaff(Tutor):
    employer = models.CharField(max_length=50,
                                verbose_name="Employeur ?")
    position = models.CharField(max_length=50)
    field = models.CharField(max_length=50,
                             verbose_name="Domaine ?")
    def uni_extended(self):
        ret = super(SupplyStaff,self).uni_extended()
        ret += '-Emp:' + self.employer + '-'
        ret += '-Pos:' + self.position + '-'
        ret += '-Dom:' + self.field
        return ret

    class Meta:
        verbose_name = 'SupplyStaff'


class BIATOS(Tutor):
    def uni_extended(self):
        return super(BIATOS,self).uni_extended()

    class Meta:
        verbose_name = 'BIATOS'

# --- Notes sur Prof ---
#    MinDemiJournees=models.BooleanField(
#       verbose_name="Min Demi-journées?", default=False)
#    unparjour=models.BooleanField(verbose_name="Un créneau par jour?",
#                                  default=False)
# # (biatos | vacataire) => TPeqTD=false (donc 3h TP <=> 2h TD)
# # 1h CM <=> 1.5h TD
# TPeqTD = models.BooleanField()self.periode


class Student(User):  # for now: representative
    belong_to = models.ManyToManyField('base.Group',
                                       blank=True)

    def __str__(self):
        return str(self.username) + '(G:' + str(self.belong_to) + ')'
