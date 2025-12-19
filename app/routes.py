import base64
import io

import qrcode
from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('main', __name__)


def get_local_ip():
    """Get local IP address for QR code."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


@bp.route('/')
def index():
    """Trebek's main interface."""
    return render_template('trebek.html')


@bp.route('/join')
def join():
    """Jennings join and game interface."""
    return render_template('jennings.html')


@bp.route('/qr')
def qr_code():
    """Generate QR code for join URL."""
    local_ip = get_local_ip()
    port = request.host.split(':')[-1]
    url = f"http://{local_ip}:{port}/join"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({
        'qr_code': f"data:image/png;base64,{img_base64}",
        'url': url
    })


@bp.route('/display')
def display():
    """TV display interface."""
    return render_template('display.html')
