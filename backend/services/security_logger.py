import logging
import os
from datetime import datetime

_log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'security.log')
_handler = logging.FileHandler(_log_path, encoding='utf-8')
_handler.setFormatter(logging.Formatter('%(message)s'))
_logger = logging.getLogger('airfinder.security')
if not _logger.handlers:
    _logger.setLevel(logging.WARNING)
    _logger.addHandler(_handler)

def log_security_event(event: str, **kwargs):
    parts = [f"timestamp={datetime.utcnow().isoformat()}Z", f"event={event}"]
    parts += [f"{k}={v}" for k, v in kwargs.items()]
    _logger.warning(' '.join(parts))
