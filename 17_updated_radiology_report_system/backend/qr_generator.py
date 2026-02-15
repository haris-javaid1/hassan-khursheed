import qrcode
from io import BytesIO
from datetime import datetime
import random
import socket

def generate_serial_number():
    """Generate unique serial number: RAD-20260212-1234"""
    date = datetime.now().strftime("%Y%m%d")
    random_num = random.randint(1000, 9999)
    return f"RAD-{date}-{random_num}"

def get_server_ip():
    """Get local LAN IP address of the server"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def create_qr_code(serial_number):
    """Create QR code image and return as bytes (generated on-the-fly)"""
    server_ip = get_server_ip()
    url = f"http://{server_ip}:8000/api/view/{serial_number}"
    
    qr = qrcode.make(url)
    
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()