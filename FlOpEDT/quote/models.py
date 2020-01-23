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


class QuoteType(models.Model):
    name = models.CharField(max_length=40)
    abbrev = models.CharField(max_length=10, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Quote(models.Model):
    quote = models.CharField(max_length=400, null=True,
                             blank=True, default=None)
    last_name = models.CharField(max_length=40, null=True,
                                 blank=True, default=None)
    for_name = models.CharField(max_length=40, null=True,
                                blank=True, default=None)
    nick_name = models.CharField(max_length=40, null=True,
                                 blank=True, default=None)
    desc_author = models.CharField(max_length=40, null=True,
                                   blank=True, default=None)
    date = models.CharField(max_length=40, null=True,
                            blank=True, default=None)
    header = models.CharField(max_length=20, null=True,
                              blank=True, default=None)
    quote_type = models.ForeignKey('QuoteType', blank=True,
                                   null=True, default=None,
                                   on_delete=models.CASCADE)
    positive_votes = models.PositiveIntegerField(default=0)
    negative_votes = models.PositiveIntegerField(default=0)
    id_acc = models.PositiveIntegerField(default=0)

    PENDING = 'P'
    ACCEPTED = 'A'
    REJECTED = 'R'
    STATUS_CHOICES = ((PENDING, 'En attente'),
                      (ACCEPTED, 'Acceptée'),
                      (REJECTED, 'Rejetée'))
    status = models.CharField(max_length=2,
                              choices=STATUS_CHOICES,
                              default=PENDING)

    def __str__(self):
        sep = ', '
        quo = ('[' + str(self.header) + '] ' if self.header is not None else '')
        auth = ''
        if self.for_name is not None:
            auth += str(self.for_name)
            if self.last_name is not None:
                auth += ' ' + str(self.last_name)
            if self.nick_name is not None:
                auth += ' dit '
        else:
            if self.last_name is not None:
                auth += str(self.last_name)
                if self.nick_name is not None:
                    auth += ' dit '
        if self.nick_name is not None:
            auth += str(self.nick_name)
        if auth == '':
            quo += str(self.quote)
        else:
            quo += '\u00AB ' + str(self.quote) + ' »'
        return (quo
                + (sep + auth if auth != '' else '')
                + (sep + str(self.desc_author) if self.desc_author is not None else '')
                + (sep + str(self.date) if self.date is not None else ''))
