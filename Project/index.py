import math
from datetime import date
import hashlib

import cloudinary.uploader
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from Project import login, dao, utils, app, db
from Project.forms import LoginForm, AddUserForm
from Project.decorator import role_only
from Project.models import Role, User, Grade, Class, Students_Classes, Score, TypeOfScore


@login.user_loader
def user_load(user_id):
    return dao.load_user(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        if session.get('role') == 'admin':
            return redirect('/admin')
        return redirect(url_for("auth"))

    return redirect(url_for("user_login"))


@app.route("/login", methods=["POST", "GET"])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    msg = ""
    if form.is_submitted() and request.method == "POST":
        username, password, user_type = form.username.data, form.password.data, form.userType.data
        user = utils.check_user(username, password, user_type)
        if user and session.get('role'):
            login_user(user)
            return redirect(url_for("index"))
        msg = "Đăng nhập thất bại"
    return render_template("login.html", msg=msg, form=form)


@app.route("/home/")
@login_required
def auth():
    return render_template("menu.html")


@app.route('/employee/quan_ly_sinh_vien')
@login_required
@role_only('employee')
def student_management():
    kw, grade, page = request.args.get('kw'), request.args.get('grade'), request.args.get("page", 1)
    students = dao.load_all_student(grade=grade, kw=kw, page=page)
    total = dao.load_student_count()
    tags = utils.page_tags(total, page)
    return render_template('employee/StudentManagement.html', stuList=students, tags=tags)


@app.route('/employee/them_hoc_sinh')
@login_required
@role_only('employee')
def add_student():
    form = AddUserForm()
    session_pending = session.setdefault('pending_users', {'msg': {}, 'total': 0})
    users_pending = [v for k, v in session_pending.items() if k not in ['msg', 'total']]
    return render_template('employee/AddStudent.html', form=form, users_pending=users_pending,
                           msg=session_pending['msg'], amount=session_pending['total'])


@app.route('/employee/xet_len_lop')
@login_required
@role_only('employee')
def upgrade_students():
    previous_semester = dao.get_previous_semester()
    students = dao.load_all_student(semester=previous_semester.id)
    curSemester = dao.get_lastest_semester()
    stuList = [(s, format(utils.overall_score(s.user_id, previous_semester.year), '.2f')) for s in students]
    return render_template("employee/UpStudent.html", students=stuList, curSemester=curSemester,
                           preSemester=previous_semester)


@app.route('/employee/quan_ly_lop_hoc')
@login_required
@role_only('employee')
def class_management():
    kw, grade, page = request.args.get('kw'), request.args.get('grade'), request.args.get("page", 1)
    classes = dao.load_all_classes(grade=grade, kw=kw, page=page)
    total = dao.load_classes_count()
    tags = utils.page_tags(total, page)
    return render_template('employee/ClassManagement.html', clsList=classes, tags=tags)


@app.route('/employee/them_lop_hoc', methods=['GET', 'POST'])
@login_required
@role_only('employee')
def add_classes():
    return render_template('employee/AddClass.html')


@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/user/<user_id>")
@login_required
def info(user_id):
    user = dao.load_user(user_id)
    role = None
    student_class = ""

    for r in user.roles:
        if r.role == Role.student:
            role = Role.student.value
            student_class = dao.get_lastest_class_of_student(user.id)
            student_class = student_class.name if student_class else "Chưa được xếp lớp"
            break
        if r.role == Role.teacher:
            role = Role.teacher.value

    return render_template('user_detail.html', Role=Role, user=user, role=role, student_class=student_class)


@app.route("/class/<class_id>")
@login_required
def class_info(class_id):
    myClass = dao.load_class(class_id)
    isEditable = (Role[session.get('role')] == Role.employee and myClass.active)
    teachers = dao.load_non_homeroom_teacher(myClass.year)
    subjects = dao.load_all_subject(myClass.grade, non_plan=True, class_id=myClass.id)
    content = f'{dao.load_student_count(myClass.id)}/{myClass.amount}'
    return render_template('class_detail.html', myClass=myClass, isEditable=isEditable, teachers=teachers,
                           subjects=subjects, student_count=content)


@app.context_processor
def common_things():
    missions, msg = [], ""
    if current_user.is_authenticated:
        role = session.get('role')
        if role == 'employee':
            msg = f"Xin chào nhân viên {current_user.name}"
            missions = [
                {'name': 'Quản lý sinh viên', 'link': "/employee/quan_ly_sinh_vien"},
                {'name': 'Quản lý lớp', 'link': '/employee/quan_ly_lop_hoc'},
            ]
        elif role == 'teacher':
            msg = f"Xin chào giáo viên {current_user.name}"
            missions = [
                {'name': 'Nhập điểm', 'link': '/teacher/nhap_diem'},
                {'name': 'Xuất Điểm', 'link': '/teacher/xuat_diem'},
            ]
    return {'missions': missions, 'msg': msg, 'Role': Role}


@app.route('/api/user_pending', methods = ["POST"])
@login_required
def pending():
    list = session.get('pending_users')
    age_start = dao.load_name_rule("AGE_START")
    age_end = dao.load_name_rule("AGE_END")

    name = request.form.get('name')
    gender = int(request.form.get('gender'))
    image = request.files.get('image')
    birthdate = request.form.get('birthdate')
    address = request.form.get('address')
    email = request.form.get('email')
    phone = request.form.get('phone')
    grade = request.form.get('grade')
    birthyear = int(birthdate[:4])
    birthmonth = int(birthdate[5:7])
    birthday = int(birthdate[8:10])
    acceptable = True
    error = ""


    age = date.today().year - birthyear
    if age < int(age_start.data) or age > int(age_end.data):
        acceptable = False
        error = "Số tuổi không đúng quy định"

    for i in range(1, list['total']+1):
        if list[str(i)]['name'] == name:
            acceptable = False
            error = "Người dùng đã được thêm vào hàng chờ"
    if utils.check_user_by_name(name):
        acceptable = False
        error = "Tên người dùng đã tồn tại"



    if not acceptable:
        list['msg'] = {
            'status': "failed",
            'message': error
        }
    else:
        if image:
            res = cloudinary.uploader.upload(image)
            image = res['secure_url']
        else:
            image = "https://res.cloudinary.com/dzm6ikgbo/image/upload/v1703999894/okrajh0yr69c5fmo3swn.png"
        list[str(list["total"]+1)] = {
            'id': list["total"]+1,
            'name': name,
            'gender': gender,
            'image': image,
            'birthdate': f'{birthday}-{birthmonth}-{birthyear}',
            'address': address,
            'email': email,
            'phone': phone,
            'grade': grade
        }
        list['msg'] = {
            'status': "success",
            'message': "Người dùng được thêm vào hàng chờ"
        }
    list['total'] = len(list)-2
    session['pending_users'] = list
    return redirect(url_for("add_student"))


@app.route('/api/user_pending/<string:user_id>', methods=['DELETE'])
@login_required
def pending_delete(user_id):
    try:
        users = session['pending_users']
        del users[user_id]
        session['pending_users'] = users
        msg = {'status': 'success', 'message': 'Xóa thành công'}
    except Exception as exc:
        msg = {'status': 'failed', 'message': str(exc)}
    return jsonify(msg)


@app.route('/api/upload', methods=["POST"])
def upload():
    try:
        res = cloudinary.uploader.upload(request.files['file'])
        msg = {'status': 'success', 'message': res['secure_url']}
    except Exception as exc:
        msg = {'status': 'failed', 'message': str(exc)}
    return jsonify(msg)

@app.route('/teacher/nhap_diem')
@login_required
@role_only('teacher')
def input_score():
    semesters = dao.get_semester()
    classes = dao.load_all_classes()
    teachers_subjects = dao.load_teachers_subjects()
    return render_template('/teacher/inputScore.html', semesters = semesters,
                           classes = classes, teachers_subjects = teachers_subjects, grade = Grade)

@app.route('/teacher/xuat_diem')
@login_required
@role_only('teacher')
def output_score():
    semesters = dao.load_year_of_semester()
    classes = dao.load_all_classes()
    teachers_subjects = dao.load_teachers_subjects()
    return render_template('/teacher/outputScore.html', semesters=semesters,
                           classes=classes, teachers_subjects=teachers_subjects, grade=Grade)


@app.route("/api/score_validate", methods = ["POST"])
def validate_score():
    data = request.json
    plan_id = data.get('plan_id')
    students = data.get('students')
    semester_id = data.get('semester_id')
    class_id = data.get('class_id')
    myClass = dao.load_class(class_id)
    failed = {
         "status": "failed",
         "message": ""
    }
    success = {
         "status": "success",
         "message": "Xác nhận thành công"
    }
    for s in students:
        score_label = dao.load_score_of_student(plan_id, int(s['id']), semester_id)

        if score_label is None:
            try:
                score_label = Score(plan_id = plan_id, student_id = int(s['id']), semester_id = semester_id)
                db.session.add(score_label)
                db.session.commit()
            except Exception as exc:
                msg = failed
                msg['message'] = str(exc)
                return jsonify(msg)
        if len(score_label.details) > 0:
            for s_d in score_label.details:
                match s_d.score_type:
                    case TypeOfScore.M15:
                        utils.update_score_record(s_d, s['m15'])
                    case TypeOfScore.M45:
                        utils.update_score_record(s_d, s['m45'])
                    case TypeOfScore.FN:
                        utils.update_score_record(s_d, s['fn'])

        utils.add_score_record(s['m15'], TypeOfScore.M15, score_label)
        utils.add_score_record(s['m45'], TypeOfScore.M45, score_label)
        utils.add_score_record(s['fn'], TypeOfScore.FN, score_label)
    msg = success
    return jsonify(msg)

@app.route("/api/subjects/<grade>")
def subject_of_grade(grade):
    grade = Grade[grade]
    subjects = dao.load_all_subject(grade=grade)
    res = []
    for s in subjects:
        temp = {
            'id' : s.id,
            'name': s.name
        }
        res.append(temp)
    return jsonify(res)

@app.route("/api/change_password/<user_id>", methods = ["POST"])
def change_password(user_id):
    data = request.json
    oldPw = data.get("old")
    newPw = data.get("new")
    user = dao.load_user(user_id)
    if hashlib.md5(oldPw.encode("utf-8")).hexdigest() == user.password:
        user.password = hashlib.md5(newPw.encode("utf-8")).hexdigest()
        db.session.commit()
        msg = {
            "message": "Cập nhật thành công"
        }
    else:
        msg = {
            "message": "Mật khẩu không đúng, vui lòng thử lại"
        }
    return jsonify(msg)

@app.route('/api/change_avatar/<user_id>', methods = ["POST"])
def change_avt(user_id):
   file = request.files.get('newFile')
   user = dao.load_user(user_id)
   if file:
        image = cloudinary.uploader.upload(file)
        path = image['secure_url']
        oldPath = user.image.split("/")
        public_id = oldPath[-1][:-4]
        user.image = path
        cloudinary.uploader.destroy(public_id)
        db.session.commit()
   return redirect(f'/user/{user_id}')

if __name__ == "__main__":
    from Project.admin import *
    app.run()
