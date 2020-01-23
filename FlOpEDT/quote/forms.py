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



from django.utils.translation import gettext_lazy as _

from django.forms import ModelForm, Textarea
from .models import Quote

from django.utils.safestring import mark_safe


class QuoteForm(ModelForm):
    class Meta:
        model = Quote
        fields = ['quote', 'last_name', 'for_name', 'nick_name', 'desc_author', 'date', 'header', 'quote_type']
        labels = {
            'quote': _('Citation '),
            'last_name': _('Nom '),
            'for_name': _('Prénom '),
            'nick_name': _('Pseudo '),
            'desc_author': mark_safe(_("Fonction, description<br/> de l'auteur/autrice ")),
            'date': _('Date '),
            'header': _('En-tête '),
            'quote_type': _('Catégorie '),
        }
        required = {
            'last_name': False,
            'for_name': False,
            'nick_name': False,
            'desc_author': False,
            'date': False,
            'header': False,
            'quote_type': False,
        }
        widgets = {
            'quote': Textarea(attrs={'cols': 60, 'rows': 5}),
        }
