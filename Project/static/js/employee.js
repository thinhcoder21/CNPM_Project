// Xóa sinh viên khỏi danh sách
function delete_from_list(id, obj) {
    if (confirm("Bạn chắc chắn muốn xóa") == true) {  // Hiển thị hộp thoại xác nhận
        obj.disabled = true;  // Vô hiệu hóa nút
        fetch(`/api/user_pending/${id}`, {  // Gửi yêu cầu DELETE tới API
            method: 'DELETE'
        }).then(function(res) {
            return res.json();  // Chuyển đổi phản hồi thành JSON
        }).then(function(data) {
            console.log(data);  // In phản hồi ra console
            obj.disabled = false;  // Kích hoạt lại nút
            document.getElementById(id).style.display = "none";  // Ẩn phần tử trong DOM
        });
    }
}

// Xác nhận sinh viên
function validate(id, obj) {
    if (confirm("Xác nhận lưu học sinh này?") == true) {  // Hiển thị hộp thoại xác nhận
        obj.disabled = true;  // Vô hiệu hóa nút
        fetch(`/api/validate_user/${id}`, {  // Gửi yêu cầu POST tới API
            method: 'POST'
        }).then(function(res) {
            return res.json();  // Chuyển đổi phản hồi thành JSON
        }).then(function(data) {
            console.log(data);  // In phản hồi ra console
            obj.disabled = false;  // Kích hoạt lại nút
            if (data['status'] == "success")
                document.getElementById(id).style.display = "none";  // Ẩn phần tử trong DOM nếu thành công
            alert(data['message']);  // Hiển thị thông báo
        });
    }
}

// Xác nhận tất cả sinh viên trong hàng chờ
function validate_all(obj) {
    if (confirm("Xác nhận sao lưu tất cả học sinh trong hàng chờ") == true) {  // Hiển thị hộp thoại xác nhận
        obj.disabled = true;  // Vô hiệu hóa nút
        fetch('/api/validate_user', {  // Gửi yêu cầu POST tới API
            method: 'POST'
        }).then(function(res) {
            return res.json();  // Chuyển đổi phản hồi thành JSON
        }).then(function(data) {
            obj.disabled = false;  // Kích hoạt lại nút
            console.log(data);  // In phản hồi ra console
            if (data['status'] == 'failed')
                alert(data['message']);  // Hiển thị thông báo lỗi
            else {
                alert("Lưu hoàn thành");  // Hiển thị thông báo thành công
                for (var i = 1; i <= data['success'].length; i++)
                    document.getElementById(i).style.display = 'none';  // Ẩn các phần tử trong DOM
            }
        });
    }
}

// Lấy danh sách sinh viên chưa thuộc lớp theo khối
function get_non_class_user_by_grade() {
    grade = document.getElementById('grade').value;  // Lấy giá trị khối lớp
    console.log(grade);
    if (grade != "NULL")
        fetch(`/api/non_class_student/${grade}`)  // Gửi yêu cầu GET tới API
        .then(function(res) {
            return res.json();  // Chuyển đổi phản hồi thành JSON
        }).then(function(data) {
            document.getElementById('amount').value = data.length;  // Cập nhật số lượng sinh viên
            let html = "";
            for (var i = 0; i < data.length; i++) {
                html += `<li class="list-group-item" style="height: 20%; display: flex; justify-content: space-between">
                    <div style="width: 5%">${data[i]['id']}</div>
                    <div style="width: 20%">${data[i]['name']}</div>
                    <div style="width: 10%">Khối ${data[i]['grade']}</div>
                    <div style="width: 20%">${data[i]['semester']}</div>
                </li>`;
            }
            document.getElementById('student_panel_get').innerHTML = html;  // Cập nhật danh sách sinh viên trong DOM
            console.log(data);
        });
    else {
        document.getElementById('amount').value = "";
        document.getElementById('student_panel_get').innerHTML = "<h2 style='display: flex; justify-content: center; align-items: center'>Vui lòng chọn khối lớp</h2>";
    }
}

// Thay đổi giáo viên của lớp
function change_teacher(id_class) {
    teacher = document.getElementById('teacher_id').value;  // Lấy ID giáo viên
    console.log(teacher);
    if (confirm("Xác nhận thay đổi") == true) {  // Hiển thị hộp thoại xác nhận
        fetch(`/api/change_class/${id_class}`, {  // Gửi yêu cầu PUT tới API
            method: "PUT",
            body: JSON.stringify({
                'change': "teacher",
                "teacher_id": teacher
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
            location.reload();  // Tải lại trang
        });
    }
}

// Khóa/mở khóa lớp
function toggleLockClass(id_class) {
    if (confirm("Xác nhận thay đổi") == true) {  // Hiển thị hộp thoại xác nhận
        fetch(`/api/change_class/${id_class}`, {  // Gửi yêu cầu PUT tới API
            method: "PUT",
            body: JSON.stringify({
                'change': "active",
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
            location.reload();  // Tải lại trang
        });
    }
}

// Lấy danh sách giáo viên theo môn học
function subjectTeacher(subject_id, id) {
    fetch(`/api/subject_teacher/${subject_id}`)  // Gửi yêu cầu GET tới API
    .then(res => res.json()).then(function(data) {
        let html = "<option value=''>Chọn giáo viên</option>";
        for (var i = 0; i < data.length; i++)
            html += `<option value='${data[i]['id']}'>${data[i]['name']}</option>`;
        document.getElementById(id).innerHTML = html;  // Cập nhật danh sách giáo viên trong DOM
    });
}

// Cập nhật danh sách giáo viên khi thay đổi môn học
function subject_teacher_on_change(id_src, dest) {
    subject_id = document.getElementById(id_src).value;  // Lấy ID môn học
    subjectTeacher(subject_id, dest);  // Gọi hàm subjectTeacher để cập nhật danh sách giáo viên
}

// Cập nhật giáo viên cho kế hoạch môn học
function update_plan_teacher(subject_id, class_id) {
    if (confirm("Xác nhận thay đổi") == true) {  // Hiển thị hộp thoại xác nhận
        teacher_id = document.getElementById(`subject_teacher_${subject_id}`).value;  // Lấy ID giáo viên
        if (teacher_id == "") return;
        console.log(teacher_id);
        fetch(`/api/change_class/${class_id}`, {  // Gửi yêu cầu PUT tới API
            method: "PUT",
            body: JSON.stringify({
                'change': "teacher_subject",
                'teacher_id': teacher_id,
                'subject_id': subject_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
        });
    }
}

// Hiển thị chế độ chỉnh sửa kế hoạch môn học
function Edit() {
    document.getElementById(`plan_edit_btn`).style.display = "none";  // Ẩn nút chỉnh sửa
    document.getElementById(`plan_exit_btn`).style.display = "block";  // Hiển thị nút thoát
    document.getElementById(`plan_edit`).style.display = "block";  // Hiển thị phần chỉnh sửa
    document.getElementById(`plan_result`).style.display = "none";  // Ẩn phần kết quả
}

// Thoát chế độ chỉnh sửa và tải lại trang
function Exit() {
    location.reload();  // Tải lại trang
}

// Xóa môn học khỏi kế hoạch
function delete_plan(subject_id, class_id) {
    if (confirm("Xác nhận xóa môn này!")) {  // Hiển thị hộp thoại xác nhận
        fetch(`/api/change_class/${class_id}`, {  // Gửi yêu cầu DELETE tới API
            method: "DELETE",
            body: JSON.stringify({
                'change': "subject",
                'subject_id': subject_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
            document.getElementById(`plan_subject${subject_id}`).style.display = "none";  // Ẩn phần tử trong DOM
        });
    }
}

// Tạo kế hoạch môn học mới
function create_new_plan(class_id) {
    if (confirm("Xác nhận thêm môn này!")) {  // Hiển thị hộp thoại xác nhận
        subject_id = document.getElementById("subject_select").value;  // Lấy ID môn học
        teacher_id = document.getElementById("teacher_select").value;  // Lấy ID giáo viên
        console.log(subject_id, teacher_id);
        fetch(`/api/change_class/${class_id}`, {  // Gửi yêu cầu POST tới API
            method: "POST",
            body: JSON.stringify({
                'change': "subject",
                'subject_id': subject_id,
                'teacher_id': teacher_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
            location.reload();  // Tải lại trang
        });
    }
}

// Xóa sinh viên khỏi lớp
function delete_student(class_id, student_id) {
    if (confirm("Xóa học sinh này?")) {  // Hiển thị hộp thoại xác nhận
        fetch(`/api/change_class/${class_id}`, {  // Gửi yêu cầu DELETE tới API
            method: "DELETE",
            body: JSON.stringify({
                'change': "student",
                'student_id': student_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
            document.getElementById(`student_${student_id}`).style.display = "none";  // Ẩn phần tử trong DOM
        });
    }
}

// Thêm danh sách sinh viên vào lớp
function add_student_list(grade, year) {
    kw = document.getElementById('student_name').value;  // Lấy từ khóa tìm kiếm
    console.log(kw);
    fetch(`/api/non_class_student/${grade}?kw=${kw}`, {  // Gửi yêu cầu POST tới API
        method: "POST",
        body: JSON.stringify({
            'year': year
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((res) => res.json()).then(function(data) {
        console.log(data);
        let temp = "";
        for (var i = 0; i < data.length; i++) {
            temp += `<li  class="list-group-item" style="height: 20%; display: flex; justify-content: space-between;">
                        <input id="s${data[i].id}" onclick="add_to_student('s${data[i].id}')" class="form-check-input" type="checkbox" value="${data[i].id}">
                        <div style='width: 3%'>${data[i].id}</div>
                        <div style='width: 40%'>${data[i].name}</div>
                        <div style='width: 12%'>Khối ${data[i].grade}</div>
                        <div style='width: 30%'>${data[i].semester}</div>
                     </li>`;
        }
        document.getElementById("non_student_list").innerHTML = temp;  // Cập nhật danh sách sinh viên trong DOM
        for (var i = 0; i < student_append.length; i++)
            document.getElementById(`s${student_append[i]}`).checked = true;  // Đánh dấu các checkbox đã chọn
    });
}

// Mảng lưu trữ ID của sinh viên được chọn
var student_append = [];

// Thêm sinh viên vào mảng lưu trữ khi checkbox được chọn
function add_to_student(id) {
    let check = document.getElementById(id);  // Lấy checkbox
    if (check.checked) {
        student_append.push(parseInt(check.value));  // Thêm ID sinh viên vào mảng nếu được chọn
    } else {
        let index = student_append.indexOf(parseInt(check.value));  // Tìm vị trí của ID trong mảng
        if (index > -1)
            student_append.splice(index, 1);  // Xóa ID khỏi mảng nếu bỏ chọn
    }
    console.log(student_append);
}

// Thêm sinh viên vào lớp
function add_to_class(class_id) {
    if (student_append.length == 0) {
        alert("Vui lòng chọn sinh viên!");  // Hiển thị thông báo nếu không có sinh viên nào được chọn
        return;
    }
    if (confirm("Xác nhận thêm sinh viên?")) {  // Hiển thị hộp thoại xác nhận
        fetch(`/api/change_class/${class_id}`, {  // Gửi yêu cầu POST tới API
            method: "POST",
            body: JSON.stringify({
                'change': "student",
                'students_id': student_append,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            alert(data['message']);  // Hiển thị thông báo
            location.reload();  // Tải lại trang
        });
    }
}

// Nâng cấp học sinh lên lớp mới
function upgrade() {
    if (confirm("Xác nhận lên lớp cho tất cả học sinh?")) {  // Hiển thị hộp thoại xác nhận
        fetch("/api/upgrade_students/", {  // Gửi yêu cầu PUT tới API
            method: "PUT",
        }).then(res => res.json()).then(function(data) {
            console.log(data);
            alert(data["message"]);  // Hiển thị thông báo
        });
    }
}
