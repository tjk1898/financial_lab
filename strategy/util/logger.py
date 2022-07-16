import logging

_logger = logging.getLogger()

_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_std_fh = logging.StreamHandler()
_std_fh.setFormatter(_formatter)

_logger.addHandler(_std_fh)

_logger.setLevel(logging.DEBUG)
_logger.propagate = False

log = _logger
