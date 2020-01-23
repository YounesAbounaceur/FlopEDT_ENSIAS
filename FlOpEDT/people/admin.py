# -*- coding: utf-8 -*-


from django.contrib import admin
from base.admin import DepartmentModelAdmin

from people.models import FullStaff, SupplyStaff, BIATOS, Tutor

from import_export import resources, fields

class TutorModelAdmin(DepartmentModelAdmin):

    def get_department_lookup(self, department):
        """
        Hook for overriding default department lookup research
        """
        return {'departments': department}

    class Meta:
        app_label = 'auth'


class TutorResource(resources.ModelResource):

	class Meta:
		model = Tutor
		fields = ( "username", "first_name", "last_name", "email" )
		


admin.site.register(FullStaff, TutorModelAdmin)
admin.site.register(SupplyStaff, TutorModelAdmin)
admin.site.register(BIATOS, TutorModelAdmin)