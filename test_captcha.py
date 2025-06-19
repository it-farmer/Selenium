import easyocr
import time

# Đo thời gian
start_time = time.time()

reader = easyocr.Reader(['vi'], verbose=False)
result = reader.readtext('captcha.png', detail=0)  # detail=0 để chỉ lấy chuỗi ký tự
captcha_text = result[0] if result else ""

print(captcha_text)

# Tính và in thời gian chạy
end_time = time.time()
execution_time = end_time - start_time
print(f"Thời gian chạy: {execution_time:.2f} giây")