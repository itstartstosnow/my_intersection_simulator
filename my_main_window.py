
from my_paint_canvas import MyPaintCanvas

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon                
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMenu, QAction, QLabel

class MyMainWindow(QMainWindow):
    '''
    QMainWindow
    ├─menuBar...
    └─main_widget - central widget
      └─QHBoxLayout
        └─canvas
    '''
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Intersection simulator (under development)')
        self.setGeometry(100, 100, 900, 900) # left, top, width, height 之后再细调吧

        self.icons = {'play': QIcon("img/play-32-2c2c2c.png"), 'pause': QIcon("img/pause-32-2c2c2c.png")}

        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        
        self.main_widget = QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.canvas = MyPaintCanvas(parent=self.main_widget, mainw=self)

        layout = QHBoxLayout(self.main_widget)
        layout.addWidget(self.canvas)

    def setup_menubar(self):
        # 目前只 file 和 help，之后再加
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 Qt.CTRL + Qt.Key_Q)
        self.help_menu = QMenu('&Help', self)
        self.help_menu.addAction('&About', self.about)
        self.menuBar().addMenu(self.file_menu)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

    def setup_toolbar(self):
        self.toolbar = self.addToolBar("my_tool_bar")
        self.play_action = QAction(self.icons['pause'], "new", self)
        self.play_action.triggered.connect(self.play_triggered)
        self.toolbar.addAction(self.play_action)

    def setup_statusbar(self):
        self.step_lbl = QLabel("Timestep: 0000", self)
        self.time_lbl = QLabel("Elapsed time: 000.0 s", self)
        self.statusBar().addWidget(self.step_lbl)
        self.statusBar().addWidget(self.time_lbl)
        
    def play_triggered(self):
        if self.canvas.disp_timer.isActive(): # 播放->暂停，按键再按下是播放
            self.canvas.disp_timer.stop()
            self.canvas.veh_timer.stop()
            self.play_action.setIcon(self.icons['play'])
        else: # 暂停->播放，按键再按下是暂停
            self.canvas.disp_timer.start()
            self.canvas.veh_timer.start()
            self.play_action.setIcon(self.icons['pause'])

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QMessageBox.about(self, "About", "Todo")