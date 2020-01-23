from django.contrib import admin

class FlOpEDTAdminSite(admin.AdminSite):

    site_header = 'FlOpEDTAdmin...'
    
    def each_context(self, request):
        context = super().each_context(request)
        if hasattr(request, 'department'):
            context['site_header'] = f"FlOpEDT Admin : {request.department.name}"
        return context