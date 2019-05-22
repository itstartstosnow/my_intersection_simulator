import sys
import time
import logging

from PyQt5.QtWidgets import QApplication
from my_main_window import MyMainWindow

if __name__ == '__main__':
    log_fname = 'log/log %s.log' % time.strftime("%Y-%m-%d %H-%M-%S")
    logging.basicConfig(filename=log_fname, format='%(message)s', level=logging.DEBUG)
    logging.debug('t, veh._id, zone, lane, x, v, a')

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    app.exec_()
