from django.shortcuts import render

from people.models import Tutor
from base.models import Group, Room

def index(request, **kwargs):
    enseignant_list = Tutor.objects.filter(is_active=True, is_tutor=True).order_by('username')
    groupe_list = Group.objects.filter(basic=True,
                                       train_prog__department=request.department)\
                               .order_by('train_prog__abbrev', 'nom')
    salle_list = [n.name.replace(' ','_') for n in Room.objects.all().order_by('name')]
    print(salle_list)
    context = { 'enseignants': enseignant_list, 'groupes':groupe_list, 'salles':salle_list }
    return render(request, 'ics/index.html', context=context)
