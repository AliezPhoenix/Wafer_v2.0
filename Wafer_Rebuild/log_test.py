import logging

class log():
    def __init__(self,name):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        stream.setLevel(logging.WARNING)

        record = logging.FileHandler(name)
        record.setLevel(logging.INFO)
        record.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(stream)
        self.logger.addHandler(record)
    def record(self,info):
        self.logger.info(info)
        self.logger.warning(info)
        self.logger.error(info)

def test_func():
    log_func = log("log_test")
    log_func.record("func")
log_test = log("log_test")
log_test.record("test")
test_func()