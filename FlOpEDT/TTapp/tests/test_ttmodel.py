
from django.test import TestCase
from unittest.mock import patch
from unittest import skip

from TTapp.TTModel import WeekDB, TTModel
import base.models as models

def mock_optimize(self, time_limit=300, solver='CBC', presolve=2):
    # mock optimize function
    print("call to mock optimize")
    return True

def mock_add_tt_to_db(target_work_copy):
    pass    

class TTModelTestCase(TestCase):

    fixtures = ['dump.json']

    @skip("redondant testting")
    def test_init(self):   
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TTModel(tp1.department.abbrev, 39, 2018, train_prog=tp1)
        self.assertIsNotNone(tt)

    @skip("redondant testting")
    @patch('TTapp.TTModel.TTModel.optimize', side_effect=mock_optimize)
    @patch('TTapp.TTModel.TTModel.add_tt_to_db', side_effect=mock_add_tt_to_db)
    def test_solve_without_optimize(self, optimize, add_tt_to_db):        
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TTModel(tp1.department.abbrev, 39, 2018, train_prog=tp1)
        tt.solve(time_limit=300, solver='CBC')
        self.assertTrue(True)

    def test_solve(self):
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        tt = TTModel(tp1.department.abbrev, 39, 2018, train_prog=tp1)
        tt.solve(time_limit=300, solver='CBC')
        self.assertTrue(True)        