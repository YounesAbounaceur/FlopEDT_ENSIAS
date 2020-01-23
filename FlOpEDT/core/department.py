from base.models import Department, TrainingProgramme, \
                        CourseType, CourseModification, CoursePreference, \
                        Dependency, Module, Group, PlanningModification, \
                        ScheduledCourse

from base.models import BreakingNews, Period, GroupType, \
                        TutorCost, UserPreference, Course, TrainingHalfDay,\
                        Room, RoomGroup, RoomPreference, RoomType, RoomSort

from people.models import Tutor


def get_model_department_lookup(model, department, field_name=None):
    """
    Get filter to apply for department filtering 
    of model instances depending on their fields 
    """
    lookup = None

    # Look for a direct relation with Department model
    for field in model._meta.get_fields():
        if not field.auto_created and  \
            field.related_model and field.related_model == Department:
            if hasattr(field, 'many_to_one') and field.many_to_one:
                lookup = field.name
                break

    if not lookup:
        # Look for a predefined lookup path
        lookups_by_model = {
            Course:'type__department',
            CourseModification: 'cours__type__department',
            CoursePreference: 'train_prog__department',
            ScheduledCourse: 'cours__type__department',
            Dependency: 'cours1__type__department',
            Module: 'train_prog__department',
            Group: 'train_prog__department',
            Room: 'subroom_of__types__department',
            RoomGroup: 'types__department',
            RoomPreference: 'room__subroom_of__types__department',
            RoomSort: 'for_type__department',
            TrainingHalfDay: 'train_prog__department',
            Tutor: 'departments',
            PlanningModification: 'cours__type__department',
            UserPreference: 'user__departments',
        }
        
        lookup = lookups_by_model.get(model, None)

    if lookup:
        if field_name:
            lookup_name = f"{field_name}__{lookup}"
        else:
            lookup_name = lookup

        return {lookup_name: department}

    return {}