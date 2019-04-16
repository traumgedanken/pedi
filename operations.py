from image_manipulator import *


class Operations:
    __all_operations = {
        'resize': [ImageResizer, None],
        'rotate': [ImageRotator, None],
        'flip': [ImageFliper, None],
        'filter': [ImageFilterer, None],
        'brightness': [ImageBrightener, None],
        'contrast': [ImageContraster, None],
        'sharpness': [ImageSharpner, None]
    }

    def __has_operation(self, name):
        return bool(Operations.__all_operations[name][1])

    def __create_operation(self, name):
        instance = Operations.__all_operations[name][0]()
        Operations.__all_operations[name][1] = instance

    def __get_instance(self, name):
        return Operations.__all_operations[name][1]

    __filters_name = ['sepia', 'black_white', 'negative']

    def get_operation(self, name):
        if (not self.__has_operation(name)):
            self.__create_operation(name)
        return self.__get_instance(name)
