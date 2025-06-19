import os
os.environ['OPENSSL_DIR'] = r'C:\Program Files\OpenSSL-Win64'
import ssl
print(ssl.OPENSSL_VERSION)