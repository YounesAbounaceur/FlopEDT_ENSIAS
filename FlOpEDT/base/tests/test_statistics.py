from django.test import TestCase
from django.core.management import call_command

import base.models as models
from base.core.statistics import    get_room_activity_by_day, \
                                    get_holidays_weeks, \
                                    get_holiday_list

from base.core.period_weeks import PeriodWeeks


class StatisticsRoomTestCase(TestCase):

    fixtures = ['dump.json']

    @classmethod
    def setUpTestData(cls):
        call_command('migrate')

    def test_room_occupancy_rate(self):
        department = models.Department.objects.get(pk=1)
        get_room_activity_by_day(department, 2018)
        self.assertTrue(True)

    def test_get_holidays_weeks(self):
        period = PeriodWeeks(2018)
        holidays = list(get_holidays_weeks(period))
        self.assertIn(44, holidays)

    def test_get_holiday_list(self):
        # May, 1, 2019
        wednesday, _ = models.Day.objects.get_or_create(day=models.Day.WEDNESDAY)
        holiday, _ = models.Holiday.objects.get_or_create(year=2019, week=19, day=wednesday)
        period = PeriodWeeks(2018)
        holiday_list = list(get_holiday_list(period))
        self.assertIn((holiday.year, holiday.week, holiday.day.no), holiday_list)

    