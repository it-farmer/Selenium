from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Đo thời gian
start_time = time.time()

username = "0909484509" 
password = "Mbf123456@" 

# Thiết lập ChromeDriver
options = webdriver.ChromeOptions() 
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

    #Chỉ lấy tháng 5
    time.sleep(1)
        # 3. Tìm tất cả các nút download hóa đơn
    download_buttons = driver.find_element(By.CLASS_NAME, "btn-download-hd")
    driver.execute_script("arguments[0].click();", download_buttons)  # Sử dụng JavaScript để click
        
    # Chọn nút download XML
    xml_button = driver.find_element(By.CSS_SELECTOR, "div.btn-download-HDDT[loaihd='XML']")
    xml_button.click()

    time.sleep(1)
    #4 duyệt qua tất cả các trang
    # while True:
    #     time.sleep(3)
    #     # 3. Tìm tất cả các nút download hóa đơn
    #     download_buttons = driver.find_elements(By.CLASS_NAME, "btn-download-hd")
    #     for btn in download_buttons:
    #         driver.execute_script("arguments[0].click();", btn)  # Sử dụng JavaScript để click
            
    #         # Chờ modal xuất hiện
    #         # time.sleep(2)
            
    #         # Chọn nút download XML
    #         xml_button = driver.find_element(By.CSS_SELECTOR, "div.btn-download-HDDT[loaihd='XML']")
    #         xml_button.click()
            
    #         # Chờ file tải xong
    #         # time.sleep(2)

    #         driver.find_element(By.XPATH, "//*[@id='modalDownLoadHoaDon']/div/div/div[1]/div[2]").click()
    #         # time.sleep(2)

    #     # Kiểm tra có nút Next không
    #     try:
    #         next_btn = driver.find_element(By.CSS_SELECTOR, "a.next")
    #         if "page-number" in next_btn.get_attribute("class"):
    #             next_btn.click()
    #         else:
    #             print("Đã hết trang!")
    #             break
    #     except:
    #         print("Không tìm thấy nút Next - Đã hết trang!")
    #         break

    # time.sleep(2)
    

finally:
    # Đóng trình duyệt
    driver.quit()

# Tính và in thời gian chạy
end_time = time.time()
execution_time = end_time - start_time
print(f"Thời gian chạy: {execution_time:.2f} giây")