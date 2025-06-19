import requests

# Thông tin đăng nhập
username = "0909484509"
password = "Mbf123456@"
ma_kh = "PE13000133890"

session = requests.Session()

# 1. Đăng nhập
res = session.post(
    "https://www.evnhcmc.vn/Dangnhap/checkLG",
    data={"u": username, "p": password, "remember": "1", "token": ""},
    headers={
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.evnhcmc.vn",
        "Referer": "https://www.evnhcmc.vn/Tracuu",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }
)
if not (res.ok and res.json().get("state") == "success"):
    print("❌ Đăng nhập thất bại")
    exit()
print("✅ Đăng nhập thành công!")

# 2. Tra cứu danh sách hóa đơn
res = session.post(
    "https://www.evnhcmc.vn/Tracuu/ajax_ds_hoadon",
    data={
        "input_makh": ma_kh,
        "input_thang": "tatca",
        "input_nam": "tatca",
        "token": "",
        "page": "1"
    },
    headers={
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.evnhcmc.vn/Tracuu",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
)

data = res.json()
ds = data.get("data", {}).get("ds_hoadon", [])
if not ds:
    print("⚠️ Không tìm thấy hóa đơn.")
    exit()

# 3. Hiển thị danh sách hóa đơn
print("📄 Danh sách hóa đơn:")
for idx, hd in enumerate(ds, 1):
    print(f"{idx}. Tháng {hd['THANG']}/{hd['NAM']} - ID: {hd['ID_HOADON']} - Tổng: {hd['TONG_TIEN']}")

choice = input("Chọn số hóa đơn để tải về (ví dụ 1): ")
try:
    choice = int(choice) - 1
    assert 0 <= choice < len(ds)
except:
    print("⚠️ Giá trị chọn không hợp lệ.")
    exit()

sel = ds[choice]
xml_id = sel["ID_HOADON"]
print(f"🔽 Bạn chọn hóa đơn ID={xml_id} tháng {sel['THANG']}/{sel['NAM']}")

# 4. Tải file XML đúng cách qua POST ajax_tai_hoadon
res_xml = session.post(
    "https://www.evnhcmc.vn/Tracuu/ajax_tai_hoadon",
    data={
        "idhd": xml_id,
        "makh": ma_kh,
        "loaihd": "XML"
    },
    headers={
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.evnhcmc.vn/Tracuu",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
)

if res_xml.status_code == 200 and "<?xml" in res_xml.text:
    fname = f"hoadon_{xml_id}_{sel['THANG']}{sel['NAM']}.xml"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(res_xml.text)
    print(f"✅ Đã tải XML về: {fname}")
else:
    print("❌ Không thể tải XML.")
    print("📎 Mã trạng thái:", res_xml.status_code)
    print("📎 Nội dung phản hồi:", res_xml.text[:200])  # In thử vài dòng đầu để debug
    with open("error_response.html", "w", encoding="utf-8") as f:
        f.write(res_xml.text)
    print("📄 Đã lưu nội dung lỗi vào: error_response.html (xem bằng trình duyệt)")
