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



from django.contrib import admin

from .models import Quote, QuoteType

from django.db.models import Max
from FlOpEDT.filters import DropdownFilterAll, DropdownFilterRel, DropdownFilterCho

from import_export import resources, fields


class QuoteResource(resources.ModelResource):
    txt = fields.Field()

    def dehydrate_txt(self, quote):
        return str(quote)

    class Meta:
        Quote
        fields = ('txt')


def accept(modeladmin, request, queryset):
    next = Quote.objects.all().aggregate(Max('id_acc'))['id_acc__max'] + 1
    for q in queryset:
        q.status = Quote.ACCEPTED
        q.id_acc = next
        q.save()
        next += 1


accept.short_description = 'Accept selected quotes'


def reject(modeladmin, request, queryset):
    queryset.update(status=Quote.REJECTED, id_acc=0)


reject.short_description = 'Reject selected quotes'


class QuoteAdmin(admin.ModelAdmin):
    def strquote(o):
        return str(o)

    strquote.short_description = 'Quote'
    strquote.admin_order_field = 'id_acc'

    list_display = (strquote, 'quote_type', 'positive_votes', 'negative_votes', 'status', 'id_acc')
    ordering = ('status', 'id_acc')
    actions = [accept, reject]
    list_filter = (('quote_type', DropdownFilterRel),
                   ('status', DropdownFilterCho))


class QuoteTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbrev')


admin.site.register(Quote, QuoteAdmin)
admin.site.register(QuoteType, QuoteTypeAdmin)
