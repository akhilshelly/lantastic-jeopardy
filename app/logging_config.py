import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir: str = "logs", log_file: str = "app.log",
                  level: int = logging.INFO):
    # os.makedirs(log_dir, exist_ok=True)
    # log_path = os.path.join(log_dir, log_file)

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    root = logging.getLogger()
    root.setLevel(level)

    # Console handler (stdout)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(level)
    root.addHandler(ch)

    # Rotating file handler
    # fh = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)
    # fh.setFormatter(fmt)
    # fh.setLevel(level)
    # root.addHandler(fh)

    # Optional: reduce noisy libraries, e.g. werkzeug
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
