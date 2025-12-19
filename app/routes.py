import base64
import io
import logging

import qrcode
from flask import Blueprint, render_template, request, jsonify

logger = logging.getLogger(__name__)
bp = Blueprint('main', __name__)


def get_local_ip():
    """Get local IP address for QR code."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        logger.debug(f"Detected local IP: {ip}")
        return ip
    except Exception as e:
        logger.warning(f"Failed to detect local IP, defaulting to localhost: {e}")
        return "localhost"


@bp.route('/')
def index():
    """Trebek's main interface."""
    logger.debug(f"Trebek interface requested from {request.remote_addr}")
    return render_template('trebek.html')


@bp.route('/join')
def join():
    """Jennings join and game interface."""
    logger.debug(f"Join interface requested from {request.remote_addr}")
    return render_template('jennings.html')


@bp.route('/qr')
def qr_code():
    """Generate QR code for join URL."""
    logger.info("QR code generation requested")
    try:
        local_ip = get_local_ip()
        port = request.host.split(':')[-1]
        url = f"http://{local_ip}:{port}/join"
        logger.debug(f"Generating QR code for URL: {url}")

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        img_base64 = base64.b64encode(buf.getvalue()).decode()
        logger.info(f"QR code generated successfully for {url}")
        return jsonify({
            'qr_code': f"data:image/png;base64,{img_base64}",
            'url': url
        })
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}", exc_info=True)
        return jsonify({'error': 'Failed to generate QR code'}), 500


@bp.route('/display')
def display():
    """TV display interface."""
    logger.debug(f"Display interface requested from {request.remote_addr}")
    return render_template('display.html')
