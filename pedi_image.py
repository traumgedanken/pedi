from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import ImageQt
from image_manipulator import ImageFilterer

from abc import ABC, abstractmethod
from copy import copy

from threading import Thread
import logging


class DisplayStrategy(ABC):
    def __init__(self, parent):
        self.parent = parent

    @abstractmethod
    def display(self, pedi_image):
        pass


class LabelStrategy(DisplayStrategy):
    def display(self, pedi_image):
        pixmap = ImageQt.toqpixmap(pedi_image.qimage)

        self.parent.image_label.setPixmap(pixmap)

        logging.debug('image label updated')


class ThumbStrategy(DisplayStrategy):
    def __init__(self, parent):
        super().__init__(parent)
        self.__filterer = ImageFilterer()

    def __display_one(self, thumb, pedi_image):
        image_filtered = pedi_image.clone()
        self.__filterer.execute(image_filtered, thumb.name)

        preview_pixmap = ImageQt.toqpixmap(image_filtered.qimage)
        thumb.setPixmap(preview_pixmap)

        logging.debug('%s thumb updated' % thumb.name)

    def display(self, pedi_image):
        for thumb in self.parent:
            thread = Thread(target=self.__display_one,
                            args=(thumb, pedi_image))
            thread.start()


class ICloneable():
    @abstractmethod
    def clone(self):
        pass


class PediImage(ICloneable):
    def __init__(self, img_path):
        pixmap = QPixmap(img_path)
        self.qimage = ImageQt.fromqpixmap(pixmap)

        self.strategy = None

    @property
    def width(self):
        return self.qimage.width

    @property
    def height(self):
        return self.qimage.height

    def set_display_strategy(self, strategy):
        self.strategy = strategy

    def redraw(self, option):
        if (not self.operation):
            return
        self.operation.execute(self, option)

    def show(self):
        if (self.strategy):
            self.strategy.display(self)

    def clone(self):
        old_qimage = self.qimage
        qimage_copy = self.qimage.copy()
        self.qimage = None

        self_copy = copy(self)
        self.qimage = old_qimage

        self_copy.qimage = qimage_copy
        return self_copy

    def save(self, new_img_path):
        self.qimage.save(new_img_path)
