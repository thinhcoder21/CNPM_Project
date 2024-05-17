import enum
import hashlib
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text, Float, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from flask_login import UserMixin

from Project import db

#ENUM
class Role(enum.Enum):
    student = "học sinh"
    employee = "nhân viên"
    teacher = "giáo viên"
    admin = "quản trị viên"

class Contact(enum.Enum):
    email = "email"
    phoneNumber = "số điện thoại"

class Grade(enum.Enum):
    G10 = 10
    G11 = 11
    G12 = 12

class TypeOfScore(enum.Enum):
    M15 = 0
    M45 = 1
    FN = 2

#BASEMODEL
class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)

class User(BaseModel, UserMixin):
    family_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    gender = Column(Boolean)
    address = Column(Text)
    birthday = Column(String(10))
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    image = Column(String(100), default="")

    @hybrid_property
    def name(self):
        return self.family_name+" "+self.first_name

    student = relationship("Student", backref="student_info", lazy=True)
    employee = relationship("Employee", backref="employee_info", lazy=True)
    teacher = relationship("Teacher", backref="teacher_info", lazy=True)
    contacts = relationship('UserContact', backref = "user", lazy=True)
    roles = relationship("RoleOfUser", backref="user_info", lazy=True)
    admin = relationship("Admin", backref="admin_info", lazy=True)
class UserContact(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    contactType = Column(Enum(Contact))
    contactData = Column(String(30))

#ROLE
class RoleOfUser(BaseModel):
    user_id = Column(Integer,ForeignKey(User.id), nullable=False)
    role = Column(Enum(Role))

#ActorBase
class ActorBase(db.Model):
    __abstract__ = True

    started_date = Column(DateTime,default=datetime.now)
    active = Column(Boolean, default=True)

class Employee(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False, unique=True)

class Admin(ActorBase):
    user_id = Column(Integer,ForeignKey(User.id), primary_key=True, nullable=False, unique=True)

class Teacher(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False, unique=True)

    classes = relationship("Class", backref="teacher_detail", lazy=True)
    subject = relationship("Teachers_Subjects", backref="teacher_detail", lazy=True)
    teaching_plan = relationship("TeachingPlan", backref="teacher_detail", lazy=True)

class Semester(db.Model):
    id = Column(String(3), primary_key=True, nullable=False)
    semester = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    students = relationship("Student", backref="semester", lazy=True)
    scores = relationship("Score", backref="semester", lazy=True)

class Class(BaseModel):
    __table_args__ = (UniqueConstraint('name', 'year'),)
    name = Column(String(5), nullable=False)
    amount = Column(Integer, default=0)
    grade = Column(Enum(Grade), nullable=False)
    year = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id))

    students = relationship("Students_Classes", backref="class_detail", lazy=True)
    teaching_plan = relationship("TeachingPlan", backref="class_detail", lazy=True)

class Student(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False, unique=True)
    grade = Column(Enum(Grade), nullable=False, default=Grade.G10)
    semester_id = Column(String(3), ForeignKey(Semester.id), nullable=False)

    classes = relationship("Students_Classes", backref="student_detail", lazy=True)
    scores = relationship("Score", backref="student_detail", lazy=True)

class Students_Classes(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    student_id = Column(Integer, ForeignKey(Student.user_id), nullable=False)

class Subject(BaseModel):
    name = Column(String(20), nullable=False, unique=True)
    grade = Column(Enum(Grade), nullable=False)
    m15 = Column(Integer, default= 1)
    m45 = Column(Integer, default= 1)
    fn = Column(Integer, default= 1)

    teachers = relationship("Teachers_Subjects", backref="subject_detail", lazy=True)
    teaching_plan = relationship("TeachingPlan", backref="subject_detail", lazy=True)

class Teachers_Subjects(db.Model):
    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id'),)
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)

class TeachingPlan(BaseModel):
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)

    student_scores = relationship("Score", backref="plan_detail", lazy=True)

class Score(BaseModel):
    plan_id = Column(Integer, ForeignKey(TeachingPlan.id), nullable=False)
    student_id = Column(Integer, ForeignKey(Student.user_id), nullable=False)
    semester_id = Column(String(3), ForeignKey(Semester.id),nullable=False)

    details = relationship("ScoreDetails", backref="info", lazy=True)

class ScoreDetails(BaseModel):
    score_id = Column(Integer, ForeignKey(Score.id), nullable=False)
    score_type = Column(Enum(TypeOfScore), nullable=False)
    score = Column(Float)

class Rule(BaseModel):
    type = Column(String(20), nullable=False, unique=True)
    data = Column(Float)
    des = Column(Text)

if __name__ == "__main__":
    from Project import app
    with app.app_context():
        db.create_all()
        # u1 = User(family_name="Nguyễn Văn", first_name = "A", gender=False, address="Nha Trang", birthday="11-11-1990",
                 # username = "ntnmai", password = hashlib.md5("123456".encode("utf-8")).hexdigest())
        # db.session.add(u1)
        #db.session.commit()
        # gv1 = RoleOfUser(user_id = u1.id, role = Role.teacher)
        #db.session.add(gv1)
        #db.session.commit()
        # pcp3 = Rule(type="CLASS_AMOUNT",data=45, des ="Lớp học có tối đa 40 học sinh")
        # db.session.add(pcp3)
        # db.session.commit()
        # import hashlib
        # u1 = User(family_name="Trần", first_name = "Bình", gender = True, address = "Nha Trang", birthday = "22-11-1985",
        #           username = "binhtran85", password = hashlib.md5("123456".encode("utf-8")).hexdigest())
        # u2 = User(family_name="Nguyễn ", first_name = "An", gender=True, address="TP. Hồ Chí Minh",
        #           birthday ='15-08-1990',
        #           username="annguyen90", password=hashlib.md5('123456'.encode("utf-8")).hexdigest())
        # u3 = User(family_name="Lê", first_name = "Cường", gender=True, address="TP. Hồ Chí Minh",
        #           birthday='05-03-1992',
        #           username="cuongle92", password=hashlib.md5("123456".encode("utf-8")).hexdigest())
        # u4 = User(family_name="Phạm", first_name = "Dung", gender=False, address="Nha Trang, Khánh Hòa",
        #           birthday='30-06-1988',
        #           username="dungpham88", password=hashlib.md5("123456".encode("utf-8")).hexdigest())
        # u5 = User(family_name="Hoàng", first_name = "H", gender=True, address="TP. Hồ Chí Minh",
        #            birthday='14-12-1995',
        #            username="hh2", password=hashlib.md5("123456".encode("utf-8")).hexdigest())
        # u6 = User(family_name="Võ", first_name = "Phong", gender=False, address="Nha Trang, Khánh Hòa",
        #           birthday='09-09-1987',
        #           username="phongvo87", password=hashlib.md5("123456".encode("utf-8")).hexdigest())
        # db.session.add(u1)
        # db.session.commit()
        # db.session.add(u2)
        # db.session.commit()
        # db.session.add(u3)
        # db.session.commit()
        # db.session.add(u4)
        # db.session.commit()
        # db.session.add(u5)
        # db.session.commit()
        # db.session.add(u6)
        # db.session.commit()
        # hs2 = RoleOfUser(user_id = 11, role = Role.student)
        # hs3 = RoleOfUser(user_id = 17, role = Role.student)
        # nv1 = RoleOfUser(user_id = 12, role = Role.employee)
        # nv2 = RoleOfUser(user_id= 13, role = Role.employee)
        # ad1 = RoleOfUser(user_id = 15, role = Role.admin)
        # gv1 = RoleOfUser(user_id = 14, role = Role.teacher)
        #
        # db.session.add(gv1)
        # db.session.commit()
        # db.session.add(hs2)
        # db.session.commit()
        # db.session.add(hs3)
        # db.session.commit()
        # db.session.add(ad1)
        # db.session.commit()
        # db.session.add(nv1)
        # db.session.commit()
        # db.session.add(nv2)
        # db.session.commit()

        # student1 = Student(user_id = 17, grade = Grade.G12, semester_id = 1)
        # db.session.add(student1)
        # db.session.commit()
        # for i in range(10):
        #     db.session.add_all([no3])
        #     db.session.commit()
        # import cloudinary.uploader
        # # path = cloudinary.uploader.upload('Project/static/anonymous.png')
        # # path = cloudinary.uploader.upload('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROw75hblsK4_TpFmVKfNFNiAAonmyJ-xP1FzIIrl3XUg&s')
        # # print(path['secure_url'])
        # contact_u1_01 = UserContact(user_id = 1, contactType = Contact.email, contactData = "abc@gmail.com")
        # contact_u1_02 = UserContact(user_id = 1, contactType = Contact.phoneNumber, contactData="0365051699")
        # k21 = Semester(id = '211', semester = 1, year = '2021-2022')
        # student1 = Student(user_id = 4, grade = Grade.G10, semester_id = k21.id)
        # pcp1 = Rule(type="AGE_START", data = 15, des = "Tuổi học sinh được tiếp nhận từ 15 tuổi đến 20 tuổi")
        # pcp2 = Rule(type="AGE_END", data=20, des ="Tuổi học sinh được tiếp nhận từ 15 tuổi đến 20 tuổi")
        # db.session.add(pcp1)
        # db.session.commit()
        # db.session.add(pcp2)
        # db.session.commit()
        # class1 = Class(name="LTCS", amount=40 , grade=Grade.G10, year=2021, teacher_id = 8 , active = 1)
        # db.session.add(class1)
        # db.session.commit()
        # rule1 = Rule(type="AVG_MIN", data = 5 , des = "Điểm tối thiểu để đạt")
        # rule2 = Rule(type="MIN_SCORE_M15", data = 1, des ="Tối thiểu có 1 cột điểm 15 phút")
        # rule3 = Rule(type="MAX_SCORE_M15", data = 5, des ="Tối đa có 5 cột điểm 15 phút")
        # rule4 = Rule(type="MIN_SCORE_M45", data = 1, des ="Tối thiểu có 1 cột điểm 45 phút")
        # rule5 = Rule(type="MAX_SCORE_M45", data = 3, des ="Tối đa có 3 cột điểm 15 phút")
        # rule6 = Rule(type="SEMESTER", data = 2 , des = "mỗi năm có 2 học kỳ")
        # db.session.add(rule1)
        # db.session.commit()
        # db.session.add(rule2)
        # db.session.commit()
        # db.session.add(rule3)
        # db.session.commit()
        # db.session.add(rule4)
        # db.session.commit()
        # db.session.add(rule5)
        # db.session.commit()
        # db.session.add(rule6)
        # db.session.commit()