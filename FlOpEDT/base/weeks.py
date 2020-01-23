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

# Week numbers issues helper
# ---------------------------

import datetime

annee_courante = 2018


# monday of Week #2
def monday_w2(y):
    eve = datetime.date(y, 1, 1)
    eve_w = eve.weekday()
    if eve_w < 4:
        m = eve + datetime.timedelta(7 - eve_w)
    else:
        m = eve + datetime.timedelta(14 - eve_w)
    return m


# week comprising the next working day
def current_week():
    now = datetime.date.today()
    mond = monday_w2(now.year)
    if now.weekday() > 4:
        now = now + datetime.timedelta(2)
    delta = now - mond
    return {'semaine': 2 + (delta.days // 7), 'an': now.year}


# list of days
def num_days(y, w):
    if w == 0:
        return []
    cur_day = monday_w2(y) + datetime.timedelta(7 * (w - 2))
    day_list = []
    for d in range(5):
        day_list.append("%02d/%02d" % (cur_day.day, cur_day.month))
        cur_day += datetime.timedelta(1)
    return day_list


# More or less working weeks
def week_list():
    li = []
    if annee_courante == 2017:
        for i in list(range(36, 44)) + list(range(45, 52)):
            li.append({'semaine': i, 'an': 2017})
        for i in list(range(2, 9)) + list(range(10, 16)) + list(range(18, 31)):
            li.append({'semaine': i, 'an': 2018})
        return li
    elif annee_courante == 2018:
        for i in list(range(36, 44)) + list(range(45, 52)):
            li.append({'semaine': i, 'an': 2018})
        for i in list(range(2, 10)) + list(range(11, 17)) + list(range(19, 31)):
            li.append({'semaine': i, 'an': 2019})
        return li
    else:
        for i in list(range(36, 44)) + list(range(45, 52)):
            li.append({'semaine': i, 'an': annee_courante})
        for i in list(range(2, 10)) + list(range(11, 17)) + list(range(19, 31)):
            li.append({'semaine': i, 'an': annee_courante+1})
        return li
