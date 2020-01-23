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

from TTapp.TTModel import TTModel
from TTapp.models import MinHalfDays, max_weight

class MyTTModel(TTModel):
    def add_specific_constraints(self):
        """
        The specific constraints stored in the database are added by the TTModel class.
        If you shall add more specific ones, you may write it down here.
        """
        TTModel.add_specific_constraints(self)


    def solve(self, time_limit=3600, solver='CBC', target_work_copy=None):
        """
        If you shall add pre (or post) processing apps, you may write them down here.
        """
        TTModel.solve(self, time_limit=time_limit, solver=solver, target_work_copy=target_work_copy)
