from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time

# Đo thời gian
import time
start_time = time.time()

username = "0909484509" 
password = "Mbf123456@" 

# Thiết lập ChromeDriver
options = webdriver.ChromeOptions() 
options.add_argument("--headless")  # Chạy ở chế độ ẩn (không hiển thị giao diện)
options.add_experimental_option("prefs", {
    "download.default_directory": r"D:\Học Đại\Thực tập\16_6\Selenium\result",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
driver = webdriver.Chrome(options = options)

try:
    # 1. Mở trang web
    driver.get("https://www.evnhcmc.vn/Tracuu/HDDT")
    print(driver.title)
    
    # 2. Đăng nhập
    btnLogin = driver.find_element(By.CLASS_NAME, "click-open-poupup-login")
    btnLogin.click()

    input_username = driver.find_element(By.CLASS_NAME, "input-user")
    input_username.send_keys(username)

    input_password = driver.find_element(By.CLASS_NAME, "input-pass")
    input_password.send_keys(password)

    driver.find_element(By.CLASS_NAME, "btn-submit-login").click()

    # time.sleep(2)

    # 3. Lấy cookie từ Selenium để dùng cho requests
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    res = session.post(
        "https://www.evnhcmc.vn/Tracuu/ajax_ds_hoadon",
        data={
            "input_makh": "PE13000133890",
            "input_thang": "5",
            "input_nam": "2025",
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

    sel = ds[0]
    xml_id = sel["ID_HOADON"]

    # 4. Tải file XML đúng cách qua POST ajax_tai_hoadon
    res_xml = session.post(
        "https://www.evnhcmc.vn/Tracuu/ajax_tai_hoadon",
        data={
            "idhd": xml_id,
            "makh": "PE13000133890",
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
        fname = f"{xml_id}_hd.xml"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(res_xml.text)
        print(f"✅ Đã tải XML về: {fname}")
    else:
        print(f"❌ Không thể tải XML cho ID {xml_id}")
        print(f"📎 Mã trạng thái: {res_xml.status_code}")
        print(f"📎 Nội dung phản hồi: {res_xml.text[:200]}")

finally:
    # Đóng trình duyệt
    driver.quit()

# Tính và in thời gian chạy
end_time = time.time()
execution_time = end_time - start_time
print(f"Thời gian chạy: {execution_time:.2f} giây")