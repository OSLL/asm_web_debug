import logging
from app.core.db.manager import DBManager
import datetime
from uuid import uuid4

class LogMongoHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.setLevel('DEBUG')
        fmt = '[%(asctime)s] %(levelname)s %(module)s:%(lineno)s : %(message)s'
        fmt_date = '%d-%M-%Y T%T%Z'
        formatter = logging.Formatter(fmt, fmt_date)
        self.setFormatter(formatter)

    def emit(self, record):
        if not record.msg:
            return
        DBManager().add_log(log_id=str(uuid4()), 
                            time=datetime.datetime.now(),
                            levelname=record.levelname,
                            message=self.format(record),
                            lineno = record.lineno,
                            pathname = record.pathname)
