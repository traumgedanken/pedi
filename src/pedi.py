import sys
from PyQt5.QtWidgets import *

from ui import PediUI


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PediUI()
    sys.exit(app.exec_())
