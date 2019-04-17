from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import logging


class State(ABC):
    @staticmethod
    def run(parent):
        pass


class LicensedState(State):
    @staticmethod
    def run(parent):
        logging.debug('on licensed save state')

        path, _ = QFileDialog.getSaveFileName(parent.parent, "QFileDialog.getSaveFileName()",
                                              f"pedi_{parent.file_name}",
                                              "Images (*.png *.jpg)")
        return path


class NotLicensedState(State):
    def run(parent):
        logging.debug('on not licensed save state')

        QMessageBox.warning(parent.parent, 'Error',
                             "Login to unlock this feature")
