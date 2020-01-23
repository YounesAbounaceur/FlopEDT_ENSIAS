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

from django.contrib.admin.filters import AllValuesFieldListFilter, RelatedFieldListFilter, \
                                        ChoicesFieldListFilter, RelatedOnlyFieldListFilter
from core.department import get_model_department_lookup
from django.db.models.fields import BLANK_CHOICE_DASH

class DropdownFilterDepartmentMixin():
    def field_choices(self, field, request, model_admin, blank_choice=BLANK_CHOICE_DASH):
        
        queryset = field.related_model._default_manager.all()
        
        if hasattr(request, 'department'):
            lookup = get_model_department_lookup(field.related_model, request.department)
            if lookup:
                queryset = field.related_model._default_manager \
                                .filter(**lookup) \
                                .distinct()

        return [(x.pk, str(x)) for x in queryset]


class DropdownFilterAll(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class DropdownFilterRel(DropdownFilterDepartmentMixin, RelatedOnlyFieldListFilter):
    template = 'admin/dropdown_filter.html'


class DropdownFilterCho(DropdownFilterDepartmentMixin, ChoicesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class DropdownFilterSimple(DropdownFilterDepartmentMixin, ChoicesFieldListFilter):
    template = 'admin/dropdown_filter.html'
