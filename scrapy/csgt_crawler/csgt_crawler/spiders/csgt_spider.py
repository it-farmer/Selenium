import scrapy
from scrapy.http import FormRequest, Request
from PIL import Image, ImageEnhance
import pytesseract
import io
import os
import json
from datetime import datetime

class TrafficViolationSpider(scrapy.Spider):
    name = 'csgt'
    allowed_domains = ['www.csgt.vn']
    start_urls = ['https://www.csgt.vn/tra-cuu-phuong-tien-vi-pham.html']

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': True, 
        'RETRY_TIMES': 3,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 10,
    }

    async def start(self):
        yield Request(
            url=self.start_urls[0],
            callback=self.parse_form,
            dont_filter=True
        )

    def parse_form(self, response):
        self.logger.info("Đang chuẩn bị gửi request tra cứu...")
        yield Request(
            url='https://www.csgt.vn/lib/captcha/captcha.class.php',
            callback=self.process_captcha,
            meta={'response_url': response.url},
            dont_filter=True
        )

    def process_captcha(self, response):
        self.logger.info("Đang tải và nhận diện CAPTCHA...")
        try:
            # Lưu ảnh CAPTCHA
            captcha_image = Image.open(io.BytesIO(response.body))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs('captchas', exist_ok=True)
            captcha_path = os.path.join('captchas', f'captcha_{timestamp}.png')
            captcha_image.save(captcha_path)
            self.logger.info(f"Đã lưu ảnh CAPTCHA tại: {captcha_path}")

            # Nhận diện CAPTCHA
            captcha_text = self.recognize_captcha(captcha_image)
            self.logger.info(f"Mã CAPTCHA nhận diện: {captcha_text}")

            # Gửi form request với dữ liệu
            formdata = {
                'BienKS': '15A-499.50',
                'Xe': '1',
                'captcha': captcha_text,
                'ipClient': '9.9.9.91',
                'cUrl': '1'
            }
            self.logger.info(f"Gửi request với formdata: {formdata}")
            yield FormRequest(
                url='https://www.csgt.vn/?mod=contact&task=tracuu_post&ajax',  # Endpoint hiện tại
                formdata=formdata,
                callback=self.parse_api_response,
                headers={
                    'Referer': response.meta['response_url'],
                    'Accept': 'application/json, text/javascript, */*; q=0.01',  # Chấp nhận JSON
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                dont_filter=True
            )
        except Exception as e:
            self.logger.error(f"Lỗi khi tải hoặc nhận diện CAPTCHA: {e}")

    def parse_api_response(self, response):
        self.logger.info("Nhận response từ API tra cứu...")
        self.logger.info(f"Nội dung response: {response.text[:500]}...")  # Debug nội dung
        self.logger.info(f"Headers response: {dict(response.headers)}")  # Debug headers
        self.logger.info(f"Request URL: {response.request.url}")  # Debug URL request

        # Kiểm tra nếu response là JSON
        try:
            data = json.loads(response.text)
            self.logger.info(f"Parsed JSON response: {data}")
            if 'href' in data:
                redirect_url = data['href'].replace('\\', '')  # Xóa ký tự escape
                self.logger.info(f"Following redirect to: {redirect_url}")
                yield Request(
                    url=redirect_url,
                    callback=self.parse_page,
                    dont_filter=True,
                    meta={'handle_httpstatus_all': True}  # Xử lý tất cả status code
                )
            else:
                self.logger.warning("No href found in JSON response")
        except json.JSONDecodeError:
            self.logger.info("Response is not JSON, treating as HTML")
            # Trích xuất dữ liệu từ HTML (nếu có)
            violation_data = {
                'bien_kiem_soat': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Biển kiểm soát:")]/following-sibling::div[1]/text()').get(),
                'mau_bien': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Màu biển:")]/following-sibling::div[1]/text()').get(),
                'loai_phuong_tien': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Loại phương tiện:")]/following-sibling::div[1]/text()').get(),
                'thoi_gian_vi_pham': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Thời gian vi phạm:")]/following-sibling::div[1]/text()').get(),
                'dia_diem_vi_pham': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Địa điểm vi phạm:")]/following-sibling::div[1]/text()').get(),
                'hanh_vi_vi_pham': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Hành vi vi phạm:")]/following-sibling::div[1]/text()').get(),
                'trang_thai': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Trạng thái:")]/following-sibling::div[1]//span/text()').get(),
                'don_vi_phat_hien': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Đơn vị phát hiện vi phạm:")]/following-sibling::div[1]/text()').get(),
                'noi_giai_quyet': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Nơi giải quyết vụ việc:")]/following-sibling::div[1]/text()').get(),
                'thong_tin_lien_he': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Số điện thoại liên hệ:")]/text()').get()
            }
            cleaned_data = {key: value.strip() for key, value in violation_data.items() if value and value.strip()}
            if cleaned_data:
                yield cleaned_data
            else:
                self.logger.info("Không tìm thấy thông tin vi phạm cụ thể, kiểm tra lại selector")

    def parse_page(self, response):
        self.logger.info("Nhận response từ trang web...")
        self.logger.info(f"Nội dung response: {response.text[:500]}...")  # Debug nội dung
        self.logger.info(f"Headers response: {dict(response.headers)}")  # Debug headers
        self.logger.info(f"Request URL: {response.request.url}")  # Debug URL request
        self.logger.info(f"Status code: {response.status}")  # Debug status code

        # Kiểm tra nếu trang chứa dữ liệu hoặc tải thêm qua AJAX
        if response.status == 200:
            violation_data = {
                'bien_kiem_soat': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Biển kiểm soát:")]/following-sibling::div[1]/text()').get(),
                'mau_bien': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Màu biển:")]/following-sibling::div[1]/text()').get(),
                'loai_phuong_tien': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Loại phương tiện:")]/following-sibling::div[1]/text()').get(),
                'thoi_gian_vi_pham': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Thời gian vi phạm:")]/following-sibling::div[1]/text()').get(),
                'dia_diem_vi_pham': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Địa điểm vi phạm:")]/following-sibling::div[1]/text()').get(),
                'hanh_vi_vi_pham': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Hành vi vi phạm:")]/following-sibling::div[1]/text()').get(),
                'trang_thai': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Trạng thái:")]/following-sibling::div[1]//span/text()').get(),
                'don_vi_phat_hien': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Đơn vị phát hiện vi phạm:")]/following-sibling::div[1]/text()').get(),
                'noi_giai_quyet': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Nơi giải quyết vụ việc:")]/following-sibling::div[1]/text()').get(),
                'thong_tin_lien_he': response.xpath('//div[@id="bodyPrint123"]//div[contains(text(), "Số điện thoại liên hệ:")]/text()').get()
            }
            cleaned_data = {key: value.strip() for key, value in violation_data.items() if value and value.strip()}
            if cleaned_data:
                yield cleaned_data
            else:
                self.logger.info("Không tìm thấy thông tin vi phạm cụ thể trong trang, kiểm tra request AJAX khác")
                # Gợi ý kiểm tra DevTools để tìm request AJAX chứa bodyPrint123
                self.logger.info("Vui lòng kiểm tra DevTools (Network tab, XHR/Fetch) để tìm request chứa <div id='bodyPrint123'>")

    def recognize_captcha(self, image):
        self.logger.info("Đang nhận diện CAPTCHA với tiền xử lý...")
        # Tiền xử lý ảnh
        image = image.convert('L')  # Grayscale
        image = image.resize((image.width * 4, image.height * 4), Image.Resampling.LANCZOS)  # Tăng kích thước
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.5)  # Tăng độ tương phản
        # Chuyển thành binary với ngưỡng
        image = image.point(lambda x: 0 if x < 130 else 255, '1')  # Điều chỉnh ngưỡng
        captcha_text = pytesseract.image_to_string(image, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz')
        # Giới hạn độ dài về 6 ký tự
        captcha_text = captcha_text[:6].strip()
        return captcha_text