import requests
import os

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

# Nhập tháng và năm muốn tải (nếu để trống sẽ lấy tất cả)
input_thang = input("Nhập tháng (01-12, hoặc 'tatca'): ").strip() or "tatca"
input_nam = input("Nhập năm (vd: 2024, hoặc 'tatca'): ").strip() or "tatca"

# 2. Tra cứu danh sách hóa đơn theo tháng/năm đã chọn
res = session.post(
    "https://www.evnhcmc.vn/Tracuu/ajax_ds_hoadon",
    data={
        "input_makh": ma_kh,
        "input_thang": input_thang,
        "input_nam": input_nam,
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

print(f"📄 Đã tìm thấy {len(ds)} hóa đơn. Đang tiến hành tải...")

# Tạo thư mục lưu hóa đơn nếu chưa có
os.makedirs("hoa_don_xml", exist_ok=True)

# 3. Tải tất cả hóa đơn
for hd in ds:
    xml_id = hd["ID_HOADON"]
    thang = hd["THANG"]
    nam = hd["NAM"]
    tong = hd["TONG_TIEN"]

    print(f"🔽 Tải hóa đơn tháng {thang}/{nam} - ID={xml_id} - Tổng: {tong}")

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
        fname = f"hoa_don_xml/hoadon_{xml_id}_{thang}{nam}.xml"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(res_xml.text)
        print(f"✅ Đã lưu: {fname}")
    else:
        print(f"❌ Lỗi khi tải hóa đơn ID={xml_id}. Đã lưu phản hồi lỗi.")
        with open(f"hoa_don_xml/error_{xml_id}.html", "w", encoding="utf-8") as f:
            f.write(res_xml.text)

print("🎉 Hoàn tất quá trình tải toàn bộ hóa đơn.")
