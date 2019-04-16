from abc import ABC, abstractmethod
from PIL import Image, ImageEnhance
from color_filter import *

# constants
CONTRAST_FACTOR_MAX = 1.5
CONTRAST_FACTOR_MIN = 0.5

SHARPNESS_FACTOR_MAX = 3
SHARPNESS_FACTOR_MIN = -1

BRIGHTNESS_FACTOR_MAX = 1.5
BRIGHTNESS_FACTOR_MIN = 0.5


class ImageManipulator(ABC):
    @abstractmethod
    def execute(self, pedi_image, option):
        pass


class ImageResizer(ImageManipulator):
    def execute(self, pedi_image, option):
        pedi_image.qimage = pedi_image.qimage.resize(option)


class ImageRotator(ImageManipulator):
    def execute(self, pedi_image, option):
        angle = option

        pedi_image.qimage = pedi_image.qimage.rotate(angle, expand=True)


class ImageFliper(ImageManipulator):
    def execute(self, pedi_image, option):
        direction = option

        pedi_image.qimage = pedi_image.qimage.transpose(direction)


class ImageFilterer(ImageManipulator):
    __filters = {
        'sepia': SepiaFilter(),
        'black_white': BlackWhiteFilter(),
        'negative': NegativeFilter()
    }

    def execute(self, pedi_image, option):
        filter_name = option
        concrete_filter = ImageFilterer.__filters[filter_name]

        concrete_filter.apply(pedi_image)


class ImageBrightener(ImageManipulator):
    def execute(self, pedi_image, option):
        factor = option

        if factor > BRIGHTNESS_FACTOR_MAX or factor < BRIGHTNESS_FACTOR_MIN:
            raise ValueError("factor should be [0-2]")

        enhancer = ImageEnhance.Brightness(pedi_image.qimage)
        pedi_image.qimage = enhancer.enhance(factor)


class ImageContraster(ImageManipulator):
    def execute(self, pedi_image, option):
        factor = option

        if factor > CONTRAST_FACTOR_MAX or factor < CONTRAST_FACTOR_MIN:
            raise ValueError("factor should be [0.5-1.5]")

        enhancer = ImageEnhance.Contrast(pedi_image.qimage)
        pedi_image.qimage = enhancer.enhance(factor)


class ImageSharpner(ImageManipulator):
    def execute(self, pedi_image, option):
        factor = option

        if factor > SHARPNESS_FACTOR_MAX or factor < SHARPNESS_FACTOR_MIN:
            raise ValueError("factor should be [0.5-1.5]")

        enhancer = ImageEnhance.Sharpness(pedi_image.qimage)
        pedi_image.qimage = enhancer.enhance(factor)


def save(img, path):
    img.save(path)
