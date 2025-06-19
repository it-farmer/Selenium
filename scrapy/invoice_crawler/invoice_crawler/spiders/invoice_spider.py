import scrapy
from scrapy.http import FormRequest
import json
import os

class EvnDirectLoginSpider(scrapy.Spider):
    name = 'evn_direct_login'
    allowed_domains = ['www.evnhcmc.vn']
    start_urls = ['https://www.evnhcmc.vn/Tracuu/HDDT']

    async def start(self):
        yield scrapy.Request(
            url='https://www.evnhcmc.vn/Tracuu/HDDT',
            callback=self.parse_login_page,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

    def parse_login_page(self, response):
        self.logger.info("Đang chuẩn bị gửi request đăng nhập...")
        formdata = {
            'u': '0909484509',  # Số điện thoại
            'p': 'Mbf123456@',  # Mật khẩu
            'remember': '1',    # Ghi nhớ đăng nhập
            'token': ''         # Token rỗng
        }
        self.logger.info(f"Dữ liệu form đăng nhập: {formdata}")

        yield FormRequest(
            url='https://www.evnhcmc.vn/Dangnhap/checkLG',
            formdata=formdata,
            callback=self.after_login,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.evnhcmc.vn',
                'Referer': 'https://www.evnhcmc.vn/Tracuu',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
        )

    def after_login(self, response):
        self.logger.info("Đăng nhập thành công!")
        formdata = {
            'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$txtMaKhachHang': 'PE13000133890',
            'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$ddlKyHD': '5',  # Cần kiểm tra giá trị thực tế
            'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolder1$btnTraCuu': 'Tra cứu'
        }
        self.logger.info(f"Dữ liệu form tra cứu: {formdata}")

        yield FormRequest(
            url='https://www.evnhcmc.vn/Tracuu/HDDT',
            formdata=formdata,
            callback=self.parse_results,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )

    def parse_results(self, response):
        if 'Lỗi' in response.text:
            self.logger.error("Lỗi: Thông tin tra cứu không đúng")
            return

        formdata = {
            'input_makh': 'PE13000133890',
            'input_thang': '5',
            'input_nam': '2025',
            'token': '',
            'page': '1'
        }
        self.logger.info(f"Dữ liệu form cho ajax_ds_hoadon: {formdata}")

        yield FormRequest(
            url='https://www.evnhcmc.vn/Tracuu/ajax_ds_hoadon',
            formdata=formdata,
            callback=self.parse_hoadon_list,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.evnhcmc.vn/Tracuu',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            },
            dont_filter=True
        )

    def parse_hoadon_list(self, response):
        self.logger.info("Nhận response từ ajax_ds_hoadon")
        if response.status == 200:
            try:
                result = json.loads(response.text)
                xml_requests = []
                if 'data' in result and 'ds_hoadon' in result['data']:
                    for item in result['data']['ds_hoadon']:
                        if 'ID_HOADON' in item:
                            idhd = item['ID_HOADON']
                            makh = 'PE13000133890'
                            formdata = {
                                'idhd': idhd,
                                'makh': makh,
                                'loaihd': 'XML'
                            }
                            xml_requests.append(
                                FormRequest(
                                    url='https://www.evnhcmc.vn/Tracuu/ajax_tai_hoadon',
                                    formdata=formdata,
                                    callback=self.save_xml,
                                    meta={'file_name': f"hoa_don_{idhd}.xml"},
                                    headers={
                                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                        'X-Requested-With': 'XMLHttpRequest',
                                        'Referer': 'https://www.evnhcmc.vn/Tracuu',
                                        'Accept': 'application/xml, text/xml, */*; q=0.01'
                                    },
                                    dont_filter=True
                                )
                            )
                            self.logger.info(f"Gửi request tải XML cho ID_HOADON {idhd} với makh {makh}")
                if not xml_requests:
                    self.logger.warning("Không tìm thấy liên kết XML trong ajax_ds_hoadon")
                else:
                    self.logger.info(f"Đã gửi {len(xml_requests)} request tải XML")
                    for request in xml_requests:
                        yield request
            except json.JSONDecodeError:
                self.logger.error("Response từ ajax_ds_hoadon không phải JSON")
        else:
            self.logger.error(f"Lỗi từ ajax_ds_hoadon, status: {response.status}")

    def save_xml(self, response):
        os.makedirs('xml_files', exist_ok=True)
        file_name = response.meta['file_name']
        file_path = os.path.join('xml_files', file_name)
        if response.status == 200:
            content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore')
            if 'application/xml' in content_type or 'text/xml' in content_type:
                with open(file_path, 'wb') as f:
                    f.write(response.body)
                self.logger.info(f"Đã lưu file XML: {file_path}")
            else:
                self.logger.warning(f"Response không phải file XML, Content-Type: {content_type}, nội dung: {response.text[:200]}...")
        else:
            self.logger.error(f"Không thể lưu file {file_path}, status: {response.status}, nội dung: {response.text[:200]}...")