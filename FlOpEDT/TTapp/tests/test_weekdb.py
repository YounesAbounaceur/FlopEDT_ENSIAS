
import base.models as models

from django.test import TestCase
from TTapp.TTModel import WeekDB

class WeekDBTestCase(TestCase):

    fixtures = ['dump.json']

    def test_attributes(self):   
        tp1 = models.TrainingProgramme.objects.get(abbrev="INFO1")
        department1 = tp1.department
        wdb = WeekDB(department1, 39, 2018, [tp1])
        self.assertEqual(wdb.train_prog, [tp1])
        # self.assertEqual(list(wdb.room_groups_for_type[self.rt1]), [self.rg1])        