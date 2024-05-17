from wtforms.fields import StringField, SubmitField, PasswordField, SelectField, DateField, FileField, EmailField, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, NumberRange, Regexp , DataRequired
from datetime import datetime
from dao import get_next_id

class LoginForm(FlaskForm):
    userType = SelectField("Đăng nhập theo: ", choices=[("employee", "Nhân viên"), ("admin", "Người quản trị"), ("teacher", "Giáo viên")])
    username = StringField(validators=[InputRequired(), Length(min=1, max=15)], render_kw={"placeholder": "Tên đăng nhập"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Mật khẩu"})
    submit = SubmitField("Đăng nhập")

class AddUserForm(FlaskForm):
    name = StringField("Họ và tên: ", validators=[InputRequired()])
    gender = SelectField("Giới tính: ", validators=[InputRequired()], choices=[(1, "Nam"), (0, "Nữ")])
    address = StringField("Địa chỉ: ", validators=[InputRequired()])
    birthdate = DateField("Ngày sinh: ", validators=[InputRequired(message="Vui lòng nhập ngày sinh hợp lệ."), Regexp(r'^\d{2}-\d{2}-\d{4}$', message="Ngày sinh phải có định dạng dd-mm-yyyy.")], format="%d-%m-%Y", render_kw={"placeholder": "dd-mm-yyyy"})
    image = FileField("Hình ảnh đại diện: ")
    email = EmailField("Email: ")
    phone = StringField("Số điện thoại: ", validators=[Length(max=11), Regexp(r'^\d+$', message="Số điện thoại chỉ được chứa các chữ số.")], render_kw={"placeholder": "Chỉ chứa số"})
    grade = SelectField("Khối lớp: ", choices=[("G10", "Khối 10"), ("G11", "Khối 11"), ("G12", "Khối 12")])
    submit = SubmitField("Thêm")

class AddClassesForm(FlaskForm):
    grade = SelectField("Khối lớp: ", choices=[("G10", "Khối 10"), ("G11", "Khối 11"), ("G12", "Khối 12")])
    submit = SubmitField("Tạo Lớp")

class SubjectForm(FlaskForm):
    name = StringField('Tên môn học', validators=[DataRequired()])
    grade = SelectField('Khối lớp', choices=[("G10", "Khối 10"), ("G11", "Khối 11"), ("G12", "Khối 12")], validators=[DataRequired()])
    m15 = IntegerField('Số cột điểm 15 phút', validators=[DataRequired(), NumberRange(min=1, max=5)])
    m45 = IntegerField('Số cột điểm 45 phút', validators=[DataRequired(), NumberRange(min=1, max=3)])
    fn = IntegerField('Số cột điểm cuối kỳ', validators=[DataRequired(), NumberRange(min=1, max=1)])

class SemesterForm(FlaskForm):
    id = IntegerField('Mã học kỳ')
    semester = IntegerField('Học kỳ', validators=[DataRequired(), NumberRange(min=1, max=2)])
    year = IntegerField('Năm học', validators=[DataRequired(), NumberRange(min=2000, max=2100)])

    def validate(self):
        if not super().validate():
            return False
        if self.id.data is None:
            self.id.data = get_next_id()
        return True