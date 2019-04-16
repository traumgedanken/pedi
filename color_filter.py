from abc import ABC, abstractmethod
from PIL import ImageQt


class ColorFilter(ABC):
    @abstractmethod
    def apply(self, pedi_image):
        pass


class SepiaFilter(ColorFilter):
    def apply(self, pedi_image):
        img = pedi_image.qimage
        pix = img.load()
        for i in range(img.width):
            for j in range(img.height):
                s = sum(pix[i, j]) // 3
                k = 30
                pix[i, j] = (s+k*2, s+k, s)


class BlackWhiteFilter(ColorFilter):
    def apply(self, pedi_image):
        img = pedi_image.qimage
        pix = img.load()
        for i in range(img.width):
            for j in range(img.height):
                s = sum(pix[i, j]) // 3
                pix[i, j] = (s, s, s)


class NegativeFilter(ColorFilter):
    def apply(self, pedi_image):
        img = pedi_image.qimage
        pix = img.load()
        for i in range(img.width):
            for j in range(img.height):
                pix[i, j] = (255 - pix[i, j][0], 255 -
                             pix[i, j][1], 255 - pix[i, j][2])
