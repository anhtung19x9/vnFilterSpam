from mainWindows import Ui_Dialog
from PyQt5 import QtWidgets, uic
import sys

class MainWindows(QtWidgets.QMainWindow, Ui_Dialog):
    def __init__(self,  *args, obj=None, **kwargs):
        super(MainWindows, self).__init__(*args,*kwargs)
        self.setupUi(self)

app = QtWidgets.QApplication(sys.argv)
windows = MainWindows()
windows.show()
app.exec_()

if __name__ == '__main__':
    print('PyCharm')


