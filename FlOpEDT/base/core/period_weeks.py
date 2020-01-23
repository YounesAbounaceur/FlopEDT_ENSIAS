import datetime
from django.db.models import Q
from base.models import Course


class PeriodWeeks():
    """
    Week oriented school year description
    """    
    
    def __init__(self, department=None, year=None, start=None, end=None, exclude_empty_weeks=False):
        """    
        Parameters
        ----------
        exclude_empty_weeks : bool
            exclude weeks from lists when no courses are planned (default is False)
        """

        self .department = department

        # school year
        self.start_year = year if year else PeriodWeeks.get_current_school_year()
        self.end_year = self.start_year + 1

        # TODO : ensure that start.year corresponds to year 

        # By default, we assume that a school year starts at 
        # september, 1 and ends at juny, 30
        self.start_day = datetime.date(self.start_year, 9, 1)
        self.end_day = datetime.date(self.end_year, 6, 30)

        _, self.start_week, _ = self.start_day.isocalendar()
        _, self.end_week, _ = self.end_day.isocalendar()

        # Get the correct last year week number (52 or 53)
        _, self.max_week, _ = datetime.date(self.start_year, 12, 28).isocalendar()

        # Get weeks list for each year
        if exclude_empty_weeks:

            if not department:
                raise ValueError(f"the department argument is required for weeks exclusion deduction")

            start_weeks = PeriodWeeks.filter_empty_weeks(
                            self.department,
                            self.start_year, 
                            self.start_week, 
                            self.max_week)

            end_weeks = PeriodWeeks.filter_empty_weeks(
                            self.department,
                            self.end_year,
                            1, 
                            self.end_week)
        else:
            start_weeks = range(self.start_week, self.max_week + 1)
            end_weeks = range(1, self.end_week + 1)

        # Set final lists
        self.__period_raw = (
            (self.start_year, set(start_weeks)),
            (self.end_year, set(end_weeks)),
            )

        self.__period_weeks = self.__period_raw[0][1] | self.__period_raw[1][1]

    
    def __iter__(self):
        self.current_year_index = 0
        return self


    def __next__(self):
        index = self.current_year_index
        self.current_year_index += 1

        if index < len(self.__period_raw):
            return self.__period_raw[index]
        else:
            raise StopIteration


    def __str__(self):
        return f"School year {self.start_year}-{self.end_year}"            


    @classmethod
    def filter_empty_weeks(cls, department, year, start, end):
        """
        Exclude weeks that doesn't have any planned course 
        """        
        return Course.objects \
                .filter(
                    an=year,
                    semaine__in=list(range(start, end + 1)),
                    module__train_prog__department=department) \
                .distinct() \
                .order_by('semaine') \
                .values_list('semaine', flat=True)


    @classmethod
    def get_current_school_year(cls):
        now = datetime.datetime.now()
        # TODO find a alternative way to test the swap month
        if now.month <= 7:
            school_year = now.year - 1
        else:
            school_year = now.year
        return school_year
        

    def get_weeks(self, year=None, format=False):

        periods = None

        if year == self.start_year:
            periods = self.__period_raw[0],
        elif year == self.end_year:
            periods = self.__period_raw[1],
        else:
            periods = self.__period_raw

        if format:
            return tuple(self.format_week_list(periods, include_year=True))
        else:
            return tuple(self.format_week_list(periods, include_year=False))


    def format_week_list(self, periods, include_year=True):
        """
        Yield weeks contained in periods objects

        :param include_year: yield a tuple with the week and its related year
        """
        for period in periods:
            for week in period[1]:
                if include_year:
                    yield period[0], week
                else:
                    yield week                

    def get_raw(self):
        return self.__period_raw

    
    def get_filter(self, related_path='cours', week=None):
        """
        Return a Q filter to restrict records returned 
        by course query to a given period

        When exclude_empty_weeks parameter is set to True, the method 
        could return None if no course is planned for the period
        """
        filter = None
        for year, weeks in self.__period_raw:
            
            week_list = None
            
            if week:
                if week in weeks:
                    week_list = {week}
            else:
                week_list = weeks

            if week_list:
                kwargs = { f"{related_path}__an": year, f"{related_path}__semaine__in": week_list}

                if filter:
                    filter |= Q(**kwargs)
                else:
                    filter = Q(**kwargs)
        
        return filter
