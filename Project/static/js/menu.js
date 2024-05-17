function setPara(key, value) {
    let url = window.location.href;  // Lấy URL hiện tại của trang
    var list = url.split(/\?|&/);  // Tách URL thành mảng các phần tử, ngăn cách bởi '?' hoặc '&'
    index = url.indexOf(key);  // Tìm vị trí của 'key' trong URL

    if (index == -1) {  // Nếu 'key' không tồn tại trong URL
        if (url.indexOf("?") > -1)  // Kiểm tra xem URL đã có dấu '?' chưa
            url += `&${key}=${value}`;  // Nếu có, thêm 'key' và 'value' bằng dấu '&'
        else
            url += `?${key}=${value}`;  // Nếu chưa, thêm 'key' và 'value' bằng dấu '?'
    } else {  // Nếu 'key' đã tồn tại trong URL
        url = `${list[0]}?`;  // Khởi tạo URL mới với phần gốc trước dấu '?'
        for (i = 1; i < list.length; i++) {  // Lặp qua từng phần tử trong danh sách đã tách
            if (list[i].indexOf(key) > -1)  // Nếu phần tử chứa 'key'
                list[i] = `${key}=${value}`;  // Cập nhật phần tử với giá trị mới
            url += i < 2 ? list[i] : `&${list[i]}`;  // Xây dựng lại URL, thêm '&' giữa các phần tử
        }
    }
    window.location.href = url;  // Điều hướng tới URL mới
}
