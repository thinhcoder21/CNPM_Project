from Project import app, dao
from Project.models import *
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import logout_user, current_user
from flask import redirect, request, session, flash
from Project.forms import SubjectForm, SemesterForm

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        print("Admin route called")
        return self.render('admin/index.html', user_count = dao.user_count())


admin = Admin(app=app, name='QUẢN TRỊ VIÊN', template_mode='bootstrap4', index_view=MyAdminIndex())

class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and session.get("role") == "admin"

class EditRuleView(AuthenticatedAdmin):
    column_list = ['des', 'data']
    column_searchable_list = ['des']
    can_create = False
    can_delete = False
    column_labels = {
        'data': 'dữ liệu',
        'des' : 'quy định'
    }

    def get_query(self):
        query = super().get_query()
        return query.filter(Rule.id.in_([1,2,3,4]))

class ManageSubjectView(AuthenticatedAdmin):
    form = SubjectForm

    def on_model_change(self, form, model, is_created):
        min_m15 = dao.load_name_rule("MIN_SCORE_M15")
        max_m15 = dao.load_name_rule("MAX_SCORE_M15")
        min_m45 = dao.load_name_rule("MIN_SCORE_M45")
        max_m45 = dao.load_name_rule("MAX_SCORE_M45")
        semester = dao.load_name_rule("SEMESTER")

        acceptable = True
        error = ""

        if model.m15 < int(min_m15.data) or model.m15 > int(max_m15.data):
            acceptable = False
            error = f"Số cột điểm 15 phút không hợp lệ (tối thiểu {min_m15.data}, tối đa {max_m15.data})"
        if model.m45 < int(min_m45.data) or model.m45 > int(max_m45.data):
            acceptable = False
            error = f"Số cột điểm 45 phút không hợp lệ (tối thiểu {min_m45.data}, tối đa {max_m45.data})"
        if model.fn != 1:
            acceptable = False
            error = "Số cột điểm cuối kỳ phải là 1"
        if semester.data != 2:
            acceptable = False
            error = "Số học kỳ mỗi năm phải là 2"

        if not acceptable:
            flash(error, 'error')
            raise ValueError(error)  # Raise an error to prevent saving

        super(ManageSubjectView, self).on_model_change(form, model, is_created)

    column_list = ['name','grade','m15','m45','fn']
    column_searchable_list = ['name']
    column_labels = {
        'name' : 'Tên môn học',
        'grade' : 'Khối lớp',
        'm15' : 'Số cột điểm 15 phút ',
        'm45' : 'Số cột điểm 45 phút',
        'fn' : 'Số cột điểm cuối kì',
    }

class EditSemesterView(AuthenticatedAdmin):
    form = SemesterForm

    def on_model_change(self, form, model, is_created):
        # Kiểm tra số lượng học kỳ trong năm
        year = model.year
        existing_semesters = Semester.query.filter_by(year=year).all()

        if is_created and len(existing_semesters) >= 2:
            flash(f"Năm {year} đã có đủ 2 học kỳ.", 'error')

        # Gọi phương thức cha để tiếp tục lưu model nếu không có lỗi
        super(EditSemesterView, self).on_model_change(form, model, is_created)

    column_list = ['id','semester','year']
    column_labels = {
        'id' : 'Mã học kỳ',
        'semester' : 'Học kỳ',
        'year' : 'Năm học'
    }

class StatsView(AuthenticatedUser):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

class LogoutView(AuthenticatedUser):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')

admin.add_view(EditRuleView(Rule, db.session, name = 'Chỉnh sửa quy định'))
admin.add_view(EditSemesterView(Semester, db.session, name = 'Chỉnh sửa học kỳ'))
admin.add_view(ManageSubjectView(Subject, db.session, name = 'Quản lí môn học'))
admin.add_view(StatsView(name = 'Thống kê'))
admin.add_view(LogoutView( name = 'Đăng xuất'))