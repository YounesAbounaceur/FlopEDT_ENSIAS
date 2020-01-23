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

from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class SolveRun(models.Model):
    run_label = models.CharField(max_length=60)
    start_week =  models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True, blank=True)
    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_week =  models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(53)],
        null=True, blank=True)
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    log_file = models.CharField(null=True, default=None, max_length = 1000)
    iis_file = models.CharField(null=True, default=None, max_length = 1000)
