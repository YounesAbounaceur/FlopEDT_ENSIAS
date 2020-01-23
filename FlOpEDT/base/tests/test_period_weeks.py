import datetime
from django.test import TestCase
from unittest.mock import patch, Mock
from base.core.period_weeks import PeriodWeeks
from base.models import Department

class PeriodWeeksTestCase(TestCase):   
   
    fixtures = ['dump.json']

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.get(abbrev='info')
        cls.period_2018 = (
            (2018, {35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52}),
            (2019, {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26}))


    def test_school_year_2018(self):
        
        pw = PeriodWeeks(department=self.department, year=2018)

        for index, (year, weeks) in enumerate(pw):
            self.assertEqual(self.period_2018[index][0], year)
            self.assertSetEqual(self.period_2018[index][1], weeks)

        self.assertEqual(pw.start_year, 2018)
        self.assertEqual(pw.start_week, 35)
        self.assertEqual(pw.end_week, 26)


    def test_Q_filter_week_35(self):
        pw = PeriodWeeks(department=self.department, year=2018)
        filter_35 = pw.get_filter(week=35)
        self.assertEqual(str(filter_35), "(AND: ('cours__an', 2018), ('cours__semaine__in', {35}))")


    def test_Q_filter_week_all(self):
        pw = PeriodWeeks(department=self.department, year=2018)
        filter_all = pw.get_filter()
        self.assertEqual(str(filter_all), "(OR: (AND: ('cours__an', 2018), ('cours__semaine__in', {35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52})), (AND: ('cours__an', 2019), ('cours__semaine__in', {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26})))")


    def test_filter_not_none(self):
        pw = PeriodWeeks(department=self.department, year=1917)
        filter = pw.get_filter()
        self.assertIsNotNone(filter)


    def test_filter_none_with_exclude_empty_weeks(self):
        pw = PeriodWeeks(department=self.department, year=1917, exclude_empty_weeks=True)
        filter = pw.get_filter()
        self.assertIsNone(filter)        


    @patch('base.core.period_weeks.datetime')
    def test_get_current_school_year(self, mock_datetime):
        target_datetime = datetime.datetime(2011, 6, 21)
        mock_datetime.datetime.now = Mock(return_value = target_datetime)
        target_year = PeriodWeeks.get_current_school_year()
        self.assertEqual(target_year, 2010)

        
    def test_period_without_parameters(self):
        target_year = PeriodWeeks.get_current_school_year()
        pw = PeriodWeeks(department=self.department)
        self.assertEqual(target_year, pw.start_year)


    def test_filter_empty_weeks(self):
        year_2018_without_weeks = {36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51}
        pw = PeriodWeeks(department=self.department, year=2018, exclude_empty_weeks=True).get_raw()
        self.assertSetEqual(pw[0][1], year_2018_without_weeks)


    def test_get_weeks_full_period(self):
        pw = PeriodWeeks(year=2018)
        weeks = pw.get_weeks()
        self.assertIn(35, weeks)
        self.assertIn(51, weeks)
        self.assertIn(2, weeks)
        

    def test_get_weeks_first_year(self):
        pw = PeriodWeeks(year=2018)
        weeks = pw.get_weeks(year=2018)
        self.assertIn(35, weeks)
        self.assertIn(51, weeks)
        self.assertNotIn(2, weeks)        

        
    def test_get_weeks_formated_full_period(self):
        pw = PeriodWeeks(year=2018)
        weeks = pw.get_weeks(format=True)
        self.assertIn((2018, 35), weeks)
        self.assertIn((2018, 51), weeks)
        self.assertIn((2019, 2), weeks)


    def test_get_weeks_formated_first_year(self):
        pw = PeriodWeeks(year=2018)
        weeks = pw.get_weeks(year=2018, format=True)
        self.assertIn((2018, 35), weeks)
        self.assertIn((2018, 51), weeks)
        self.assertNotIn((2019, 2), weeks)
