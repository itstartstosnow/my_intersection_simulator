import sys

from PyQt5.QtWidgets import QApplication
from my_main_window import MyMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    app.exec_()
