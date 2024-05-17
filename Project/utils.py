import hashlib
import math

from flask import session
from flask_login import current_user

from Project import db, dao, app
from Project.models import *


def check_user(username, password, user_type):
    enc_pass = hashlib.md5(password.encode("utf-8")).hexdigest()
    user = User.query.filter(User.username == username.strip(), User.password == enc_pass).first()
    if user and user_type != "student":
        roles = RoleOfUser.query.filter(RoleOfUser.user_id == user.id).all()
        for r in roles:
            if Role[user_type] == r.role:
                session['role'] = user_type
                return user

    session['role'] = None
    return user


def check_user_by_name(name):
    return User.query.filter(User.name == name).first()


def page_tags(total, page):
    pages = math.ceil(total / app.config['CN_PAGE_SIZE'])
    page = int(page)
    if page == 1:
        tags = {'start': 1, 'end': min(pages, 3)}
    elif page == pages:
        tags = {'start': max(1, page - 2), 'end': page}
    else:
        tags = {'start': page - 1, 'end': min(page + 1, pages)}
    return tags


def update_score_record(record, scores):
    if scores:
        if scores[0] == "":
            db.session.delete(record)
        else:
            record.score = float(scores[0])
        db.session.commit()
        scores.pop(0)


def overall_score(student_id, year):
    semesters = dao.get_semester(year)
    semester_averages = []

    for semester in semesters:
        scores = Score.query.filter(Score.student_id == student_id, Score.semester_id == semester.id).all()
        subject_averages = []

        if not scores:
            return 0

        for score in scores:
            total, count = 0, 0
            for detail in score.details:
                weight = 1 if detail.score_type == TypeOfScore.M15 else 2 if detail.score_type == TypeOfScore.M45 else 3
                total += detail.score * weight
                count += weight

            average = total / count if count != 0 else 0
            subject_averages.append(average)

        semester_averages.append(sum(subject_averages) / len(subject_averages) if subject_averages else 0)

    return sum(semester_averages) / len(semester_averages) if semester_averages else 0


def add_score_record(scores, score_type, score):
    for score_detail in scores:
        if score_detail:
            temp = ScoreDetails(score_id=score.id, score_type=score_type, score=float(score_detail))
            db.session.add(temp)
            db.session.commit()


s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'


def remove_accents(input_str):
    return ''.join(s0[s1.index(c)] if c in s1 else c for c in input_str)


