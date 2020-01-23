from django.test import TestCase
from TTapp.TTUtils import basic_swap_version, basic_reassign_rooms
import base.models as models

class TTutilsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.department1 = models.Department.objects.create(name="departement1", abbrev="dept1")
        cls.department2 = models.Department.objects.create(name="departement2", abbrev="dept2")
        cls.tp1 = models.TrainingProgramme.objects.create(name="TrainingProgramme1", abbrev="tp1", department=cls.department1)
        cls.tp2 = models.TrainingProgramme.objects.create(name="TrainingProgramme2", abbrev="tp2", department=cls.department2)
        cls.gt1 = models.GroupType.objects.create(name="groupe_type_1", department=cls.department1)
        cls.g1 = models.Group.objects.create(nom="gp1", train_prog=cls.tp1, type=cls.gt1, size=0)
        cls.ct1 = models.CourseType.objects.create(name="CourseType1")
        cls.p1 = models.Period.objects.create(name="annee_complete", starting_week=0, ending_week=53)
        cls.m1 = models.Module.objects.create(nom="module1", abbrev="m1", train_prog=cls.tp1, period=cls.p1)
        cls.c1 = models.Course.objects.create(groupe=cls.g1, semaine=39, an=2018, type=cls.ct1, module=cls.m1)
        cls.day1 = models.Day.objects.create(day=models.Day.MONDAY)
        cls.t1 = models.Time.objects.create()
        cls.s1 = models.Slot.objects.create(jour=cls.day1, heure=cls.t1)
        cls.edtv1 = models.EdtVersion.objects.create(department=cls.department1, semaine=39, an=2018, version=3)
        cls.scheduled_courses = {}
        for i in range(0,9):
            cls.scheduled_courses[i] = models.ScheduledCourse.objects.create(cours=cls.c1, creneau=cls.s1, copie_travail=i)

    def test_basic_swap_version(self):   
        basic_swap_version(self.department1, 39, 2018, 2, 5)
        edt_version = models.EdtVersion.objects.get(department=self.department1, semaine=39, an=2018)
        self.assertEqual(edt_version.version, 4)
        
        for sc in self.scheduled_courses.values():
            sc.refresh_from_db()

        self.assertEqual(self.scheduled_courses[2].copie_travail, 5)
        self.assertEqual(self.scheduled_courses[5].copie_travail, 2)

    def test_basic_reassign_rooms(self):
        basic_reassign_rooms(self.department1, 39, 2018, 0)
        self.assertTrue(True)