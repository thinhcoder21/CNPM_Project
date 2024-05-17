function done() {
    // Gọi hàm validate() để kiểm tra và xác nhận điểm số
    validate();
    // Hiển thị thông báo hoàn thành
    alert("Thành công! Quá trình nhập điểm đã hoàn thành!");
}

function save() {
    // Hiển thị thông báo đã lưu vào nháp
    alert("Thành công! Đã lưu vào nháp!");
}

function deleteScore() {
    // Hiển thị thông báo đã xóa hết điểm của học sinh
    alert("Thành công! Đã xóa hết điểm của học sinh!");
}

// Gắn sự kiện onclick cho nút "btnPrint" để gọi hàm printElement
document.getElementById("btnPrint").onclick = function () {
    printElement(document.getElementById("printThis"));
}

function printElement(elem) {
    // Tạo một bản sao của phần tử cần in
    var domClone = elem.cloneNode(true);

    // Kiểm tra nếu "printSection" không tồn tại, tạo mới và thêm vào body
    var $printSection = document.getElementById("printSection");

    if (!$printSection) {
        $printSection = document.createElement("div");
        $printSection.id = "printSection";
        document.body.appendChild($printSection);
    }

    // Xóa nội dung cũ và thêm bản sao của phần tử vào "printSection"
    $printSection.innerHTML = "";
    $printSection.appendChild(domClone);
    // Gọi chức năng in của trình duyệt
    window.print();
}

// Khởi tạo các biến toàn cục
var teaching_plan_id = null;
var list_student_id = [];
var mins15 = 0, mins45 = 0, final = 0;

function init() {
    // Đặt lại các biến toàn cục
    teaching_plan_id = null;
    list_student_id = [];
    mins15 = mins45 = final = 0;
}

function resetSubject() {
    // Đặt lại nội dung dropdown môn học và khởi tạo lại các biến
    document.getElementById("subject").innerHTML = "<option selected value=''>--- MÔN HỌC ---</option>";
    init();
}

function validate() {
    if (confirm("Xác nhận chỉnh sửa điềm")) {
        var semester_id = document.getElementById("semester").value;

        if (teaching_plan_id == null) {
            alert("Vui lòng chọn lớp");
            return;
        }

        var stuList = [];
        for (let i = 0; i < list_student_id.length; i++) {
            var mins15_score = [];
            for (let j = 0; j < mins15; j++) {
                var id = `${list_student_id[i]}_15min_${j}`;
                var temp = document.getElementById(id).value;
                mins15_score.push(temp);
            }
            var mins45_score = [];
            for (let j = 0; j < mins45; j++) {
                var id = `${list_student_id[i]}_45min_${j}`;
                var temp = document.getElementById(id).value;
                mins45_score.push(temp);
            }
            var final_score = [];
            for (let j = 0; j < final; j++) {
                var id = `${list_student_id[i]}_final_${j}`;
                var temp = document.getElementById(id).value;
                final_score.push(temp);
            }
            var studentData = {
                "id": list_student_id[i],
                "mins15": mins15_score,
                "mins45": mins45_score,
                "final": final_score
            };
            stuList.push(studentData);
        }

        console.log(stuList);
        var class_id = document.getElementById("class").value;
        fetch("/api/score_validate", {
            method: "POST",
            body: JSON.stringify({
                'plan_id': teaching_plan_id,
                'semester_id': semester_id,
                'students': stuList,
                'class_id': class_id
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {
            console.log(data);
            alert(data['message']);
        });
    }
}

// Ghi chú các dòng mã bị chú thích
/*
function checkScore() {
    score_15_1_in = document.getElementById("15min-1").value
    score_preriod_1_in = document.getElementById("period-1").value
    score_midterm_in = document.getElementById("midterm").value
    if (score_15_1_in == "" || score_preriod_1_in == "" || score_midterm_in == "")
        alert("Vui lòng không bỏ sót sinh viên")
    else
        alert("Thành công! Quá trình nhập điểm đã hoàn thành!");
}
*/
