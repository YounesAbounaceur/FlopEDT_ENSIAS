# -*- coding: utf-8 -*-


from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Tutor
from .admin import TutorResource

def redirect_add_people_kind(req, kind):
    if kind == "stud":
        return redirect('people:add_student')
    elif kind == "full":
        return redirect('people:add_fullstaff')
    elif kind == "supp":
        return redirect('people:add_supplystaff')
    elif kind == "BIAT":
        return redirect('people:add_BIATOS')
    else:
        raise Http404("I don't know this kind of people.")


@login_required
def redirect_change_people_kind(req):
    if req.user.is_student:
        return redirect('people:change_student')
    if req.user.is_tutor:
        if req.user.tutor.status == Tutor.FULL_STAFF:
            return redirect('people:change_fullstaff')
        if req.user.tutor.status == Tutor.SUPP_STAFF:
            return redirect('people:change_supplystaff')
        if req.user.tutor.status == Tutor.BIATOS:
            return redirect('people:change_BIATOS')
    else:
        raise Http404("Who are you?")
            

def fetch_tutors(req):
	dataset = TutorResource().export(Tutor.objects.all())
	response = HttpResponse(dataset.csv,
                                content_type='text/csv')
	return response



