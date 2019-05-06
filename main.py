import sys
import logging

from PyQt5.QtWidgets import QApplication
from my_main_window import MyMainWindow

if __name__ == '__main__':
    logging.basicConfig(filename='log/190506.log', level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    app.exec_()
