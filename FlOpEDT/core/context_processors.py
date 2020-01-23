from django.conf import settings


def edt_context(request):
    if hasattr(request, 'department'):
        return {'department': request.department.abbrev}
    else:
        return {}