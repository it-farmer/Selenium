from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os
import easyocr
import base64

# Đo thời gian
start_time = time.time()

load_dotenv()

print(f"Thời gian chạy 1: {start_time:.2f} giây")
reader = easyocr.Reader(['vi'], verbose=False)  # Tắt thông báo của easyocr

current_time = time.time()
print(f"Thời gian chạy 2: {current_time - start_time:.2f} giây")

options = webdriver.ChromeOptions() 
options.add_argument("--headless")
options.add_argument("--no-sandbox")  # Cần thiết trên Linux
options.add_argument("--disable-dev-shm-usage")  # Khắc phục lỗi bộ nhớ
driver = webdriver.Chrome(options = options)
# driver = webdriver.Chrome()

try:
    current_time = time.time()
    print(f"Thời gian chạy 3: {current_time - start_time:.2f} giây")
    driver.get("https://www.csgt.vn/tra-cuu-phuong-tien-vi-pham.html")
    print(driver.title)

    # Tải hình ảnh CAPTCHA
    current_time = time.time()
    print(f"Thời gian chạy 4: {current_time - start_time:.2f} giây")
    captcha_element = driver.find_element(By.ID, "imgCaptcha")

    # Chuyển ảnh sang base64
    script = """
    var img = arguments[0];
    var canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);
    return canvas.toDataURL('image/png').split(',')[1];
    """
    base64_data = driver.execute_script(script, captcha_element)
    
    # Lưu ảnh từ base64
    with open("captcha.png", "wb") as f:
        f.write(base64.b64decode(base64_data))

    # Nhận diện ký tự từ hình ảnh
    current_time = time.time()
    print(f"Thời gian chạy 5: {current_time - start_time:.2f} giây")
    result = reader.readtext('captcha.png', detail=0)  # detail=0 để chỉ lấy chuỗi ký tự
    captcha_text = result[0] if result else ""

    # if not captcha_text:
    #     captcha_text = input("Nhập mã Captcha thủ công: ")

    # captcha_text = input("Nhập mã Captcha: ")
    current_time = time.time()
    print(f"Thời gian chạy 6: {current_time - start_time:.2f} giây")
    driver.find_element(By.CSS_SELECTOR, "input.input[name='txt_captcha']").send_keys(captcha_text)

    driver.find_element(By.XPATH, "//*[@id='formBSX']/div[2]/div[1]/input").send_keys(os.getenv("BIEN_KIEM_SOAT"))
    driver.find_element(By.XPATH, "//*[@id='formBSX']/div[2]/div[2]/select").send_keys(os.getenv("LOAI_PHUONG_TIEN"))

    driver.find_element(By.CLASS_NAME, "btnTraCuu").click()
    # driver.implicitly_wait(10)
    time.sleep(1)

    current_time = time.time()
    print(f"Thời gian chạy 7: {current_time - start_time:.2f} giây")
    infos = driver.find_elements(By.CLASS_NAME, "form-group")   
    for info in infos:
        spans = info.find_elements(By.TAG_NAME, "span")
        if spans:  
            label = spans[0].text  
            content = info.find_element(By.CSS_SELECTOR, "div.row > div").text
            print(label, content)
        else:
            print(info.text)

    
    current_time = time.time()
    print(f"Thời gian chạy 8: {current_time - start_time:.2f} giây")

finally:
    driver.quit()

# Tính và in thời gian chạy
end_time = time.time()
execution_time = end_time - start_time
print(f"Thời gian chạy: {execution_time:.2f} giây")
