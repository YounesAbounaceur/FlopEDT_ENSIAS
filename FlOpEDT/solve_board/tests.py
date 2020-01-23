# -*- coding: utf-8 -*-


from django.test import TestCase
from solve_board.views import get_constraints, get_pulp_solvers, get_pulp_solvers_viewmodel
from base import models as base
import pulp.solvers as solver_classes


from TTapp.models import *

def funcname(self, parameter_list):
    raise NotImplementedError

class GetPulpSolversViewModelTestCase(TestCase):

    def test_cbc(self):
        viewmodel = get_pulp_solvers_viewmodel()
        self.assertIn(('PULP_CBC_CMD', 'CBC'), viewmodel)


class GetAvailableSolversTestCase(TestCase):

    def test_coin_cmd(self):
        solvers = get_pulp_solvers(False)
        self.assertIn(solver_classes.COIN_CMD, solvers)

    def test_cbc_cmd(self):
        solvers = get_pulp_solvers(False)
        self.assertIn(solver_classes.PULP_CBC_CMD, solvers)

    def test_default_available_solver(self):
        solvers = get_pulp_solvers(True)
        self.assertIn(solver_classes.PULP_CBC_CMD, solvers)


class GetConstraintsTestCase(TestCase):

    def setUp(self):
        base.Department.objects.all().delete()

        self.department1 = base.Department.objects.create(name="departement1", abbrev="dept1")
        self.department2 = base.Department.objects.create(name="departement2", abbrev="dept2")
        self.tp1 = base.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1", department=self.department1)
        self.tp2 = base.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2", department=self.department2)
        self.ct1 = base.CourseType.objects.create(name="CourseType1")

        self.c_basic = LimitCourseTypePerPeriod.objects.create(limit=0, type=self.ct1, department=self.department1)

        self.c_2018 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp1, year=2018, limit=0, type=self.ct1, department=self.department1)
        self.c_2018_39 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp1, year=2018, week=39, limit=0, type=self.ct1, department=self.department1)
        self.c_2018_39_without_tp = LimitCourseTypePerPeriod.objects.create(year=2018, week=39, limit=0, type=self.ct1, department=self.department1)

        self.c_tp2 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp2, limit=0, type=self.ct1, department=self.department1)
        self.c_2019_1 = LimitCourseTypePerPeriod.objects.create(train_prog=self.tp2, year=2019, week=1, limit=0, type=self.ct1, department=self.department1)

    def test_week_without_train_prog(self):   
        constraints = set(get_constraints(self.department1, year=2018, week=39))
        self.assertSetEqual(constraints, set([self.c_basic, self.c_2018_39, self.c_2018_39_without_tp, self.c_tp2]))

    def test_week_without_year(self):   
        with self.assertLogs('base', level='WARNING') as cm:
            list(get_constraints(self.department1, week=39))
        self.assertIn('WARNING', cm.output[0])        

    def test_train_prog(self):   
        constraints = set(get_constraints(self.department1, train_prog=self.tp2))
        self.assertSetEqual(constraints, set([self.c_basic, self.c_tp2, self.c_2018_39_without_tp, self.c_2019_1]))

    def test_train_prog_with_week(self):   
        constraints = set(get_constraints(self.department1, train_prog=self.tp1, year=2018, week=39))
        self.assertSetEqual(constraints, set([self.c_basic, self.c_2018_39]))        