from sqlalchemy import func
from sqlalchemy.orm import validates

from Project.models import User, Role, Student, Rule, Semester, Class, Grade, \
    Students_Classes, TeachingPlan, Subject, Teacher, Teachers_Subjects, Score, ScoreDetails, TypeOfScore, RoleOfUser
from Project import app, db
import hashlib

def load_user(user_id):
    return User.query.get(user_id)

def load_all_user():
    return User.query.all()

def load_all_student(grade=None, page=None, kw=None, semester=None):
    query = db.session.query(Student).join(User)

    if semester:
        query = query.filter(Student.semester_id == semester)

    if grade:
        query = query.filter(Student.grade == Grade[grade])

    if kw:
        query = query.filter(User.name.ilike(f'%{kw}%'))

    if page:
        query = query.order_by(User.first_name.asc()).offset(page).limit(app.config['CN_PAGE_SIZE'])

    return query.all()

def load_student_count(class_id=None):
    query = Student.query

    if class_id:
        query = Students_Classes.query.filter(Students_Classes.class_id == class_id)

    return query.count()

def load_all_rules():
    return Rule.query.all()

def load_name_rule(name):
    return Rule.query.filter(Rule.type == name).first()

#semester
def get_lastest_semester():
    return Semester.query.order_by(Semester.id.desc()).first()

def get_previous_semester():
    return Semester.query.order_by(Semester.id.desc()).all()[1]

def load_non_homeroom_teacher(year):
    myIDList = db.session.query(Teacher.user_id).join(Class).filter(Class.year.__eq__(year))
    myList = db.session.query(Teacher).filter(Teacher.user_id.not_in(myIDList)).all()
    return myList

def get_semester(year=None):
    query = Semester.query

    if year:
        query = query.filter(Semester.year == year)

    return query.all()

def load_semester_by_id(id):
    return Semester.query.filter(Semester.id == id).first()

def load_year_of_semester():
    return db.session.query(Semester.year).distinct().all()

#classes
def load_all_classes(grade=None, kw=None, page=None, year=None):
    query = Class.query.order_by(Class.year.desc())

    if grade:
        query = query.filter(Class.grade == Grade[grade])

    if kw:
        query = query.filter(Class.name.ilike(f'%{kw}%'))

    if year:
        query = query.filter(Class.year == year)

    if page:
        query = query.all()
        query = query[page * app.config['CN_PAGE_SIZE']:(page + 1)* app.config['CN_PAGE_SIZE']]

    return query

def load_classes_count(year=None):
    query = Class.query

    if year:
        query = query.filter(Class.year == year)

    return query.count()

def get_lastest_class_of_student(student_id):
    year = get_previous_semester().year
    return db.session.query(Class).join(Students_Classes).filter(Students_Classes.student_id == student_id, Class.year == year).first()

def load_class(id = None, name = None):
    if id:
        return Class.query.filter(Class.id == id).first()
    if name:
        return Class.query.filter(Class.name == name).first()

    return None

def load_class_of_teacher(id, semester=None, grade=None, year=None):
    query = db.session.query(Class).join(TeachingPlan).filter(TeachingPlan.teacher_id == id)

    if semester:
        semester = load_semester_by_id(semester)
        query = query.filter(Class.year == semester.year)

    if year:
        query = query.filter(Class.year == year)

    if grade:
        query = query.filter(Class.grade == grade)

    return query.all()

def load_subject_planned_teacher(id, class_id = None):
    query = db.session.query(Subject).join(TeachingPlan).filter(TeachingPlan.teacher_id == id,
                                                               TeachingPlan.class_id == class_id).all()
    return query

def load_teacher_of_subject(id):
    return db.session.query(Teacher).join(Teachers_Subjects).filter(Teachers_Subjects.subject_id == id).all()

def load_all_subject(grade=None, non_plan=None, class_id=None):
    query = Subject.query

    if grade:
        query = query.filter(Subject.grade == grade)

    if non_plan:
        alr_subjects = db.session.query(Subject.id).join(TeachingPlan).filter(TeachingPlan.class_id == class_id)
        query = query.filter(Subject.id.not_in(alr_subjects))

    return query.all()

def load_teaching_plan(teacher_id=None, class_id=None, subject_id=None):
    query = TeachingPlan.query

    if teacher_id:
        query = query.filter(TeachingPlan.teacher_id == teacher_id)

    if class_id:
        query = query.filter(TeachingPlan.class_id == class_id)

    if subject_id:
        query = query.filter(TeachingPlan.subject_id == subject_id)

    return query.all()

def load_teachers_subjects():
    return Teachers_Subjects.query.all()

def load_score_of_student(teaching_plan_id, student_id , semester):
    return Score.query.filter(Score.plan_id == teaching_plan_id, Score.student_id == student_id , Score.semester_id == semester).first()

def user_count():
    return db.session.query(RoleOfUser.role, func.count(RoleOfUser.id)).group_by(RoleOfUser.role).all()

def get_next_id():
    from Project.models import Semester
    max_id = db.session.query(db.func.max(Semester.id)).scalar()
    return (max_id or 0) + 1

@validates('grade')
def validate_grade(self, key, grade):
    if not Class.query.filter_by(grade=grade).first():
        raise ValueError('Khối phải có ít nhất một lớp.')
    return grade