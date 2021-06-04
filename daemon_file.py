import logging
import time
import os
from daemon import runner
from datetime import datetime


class App():   
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path =  os.path.join(os.getcwd(), 'multiproto.pid')
        self.pidfile_timeout = 5
           
    def run(self):
        while True:
            # logger.debug("Debug message")
            # logger.info("Info message")
            # logger.warn("Warning message")
            # logger.error("Error message")
            logger.info(f'LOG: {datetime.now()}')
            time.sleep(5)


if __name__ == '__main__':
    app = App()
    logger = logging.getLogger("Multiprotocol Chat")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(os.path.join(os.getcwd(), "multiproto.log"))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    daemon_runner.do_action()

