from PIL import ImageQt, Image
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


# my
from pedi_image import PediImage, LabelStrategy, ThumbStrategy
from operations import Operations
from drawer import Drawer
from image_manipulator import BRIGHTNESS_FACTOR_MIN, BRIGHTNESS_FACTOR_MAX
from database import DataBase
from license_state import LicensedState, NotLicensedState


# system
import ntpath
import logging
from functools import partial
logging.basicConfig(level=logging.DEBUG)

# constants
SLIDER_MIN_VAL = -100
SLIDER_MAX_VAL = 100
SLIDER_DEF_VAL = 0
THUMB_SIZE = 120


# global
image_original = None
operations = Operations()
drawer = Drawer()
strategies = {}


class ActionTabs(QTabWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.filters_tab = FiltersTab(self)
        self.adjustment_tab = AdjustingTab(self)
        self.modification_tab = ModificationTab(self)
        self.rotation_tab = RotationTab(self)

        self.addTab(self.filters_tab, "Filters")
        self.addTab(self.adjustment_tab, "Adjusting")
        self.addTab(self.modification_tab, "Modification")
        self.addTab(self.rotation_tab, "Rotation")

        self.setMaximumHeight(190)


class FiltersTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.thumbs = [
            self.create_filter_thumb('sepia'),
            self.create_filter_thumb('black_white'),
            self.create_filter_thumb('negative')
        ]
        global strategies
        strategies['thumb'] = ThumbStrategy(self.thumbs)

        self.setLayout(self.main_layout)

    def create_filter_thumb(self, name):
        thumb_label = QLabel()
        thumb_label.name = name
        thumb_label.setStyleSheet("border:2px solid #ccc;")

        thumb_label.setToolTip(f"Apply <b>{name}</b> filter")

        thumb_label.setCursor(Qt.PointingHandCursor)
        thumb_label.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        thumb_label.mousePressEvent = partial(self.on_filter_select, name)

        self.main_layout.addWidget(thumb_label)
        return thumb_label

    def on_filter_select(self, name, e):
        logging.debug('%s filter selected' % name)

        global image_preview, drawer, operations
        operation = operations.get_operation('filter')
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, name)
        self.parent.parent.refresh_image()


class AdjustingTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        contrast_label = QLabel("Contrast")
        contrast_label.setAlignment(Qt.AlignCenter)

        brightness_label = QLabel("Brightness")
        brightness_label.setAlignment(Qt.AlignCenter)

        sharpness_label = QLabel("Sharpness")
        sharpness_label.setAlignment(Qt.AlignCenter)

        contrast_slider = QSlider(Qt.Horizontal, self)
        contrast_slider.setMinimum(SLIDER_MIN_VAL)
        contrast_slider.setMaximum(SLIDER_MAX_VAL)
        contrast_slider.sliderReleased.connect(
            self.on_contrast_slider_released)
        contrast_slider.setToolTip(str(SLIDER_MAX_VAL))

        brightness_slider = QSlider(Qt.Horizontal, self)
        brightness_slider.setMinimum(SLIDER_MIN_VAL)
        brightness_slider.setMaximum(SLIDER_MAX_VAL)
        brightness_slider.sliderReleased.connect(
            self.on_brightness_slider_released)
        brightness_slider.setToolTip(str(SLIDER_MAX_VAL))

        sharpness_slider = QSlider(Qt.Horizontal, self)
        sharpness_slider.setMinimum(SLIDER_MIN_VAL)
        sharpness_slider.setMaximum(SLIDER_MAX_VAL)
        sharpness_slider.sliderReleased.connect(
            self.on_sharpness_slider_released)
        sharpness_slider.setToolTip(str(SLIDER_MAX_VAL))

        self.sliders = {
            'brightness': brightness_slider,
            'contrast': contrast_slider,
            'sharpness': sharpness_slider
        }

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(contrast_label)
        main_layout.addWidget(contrast_slider)

        main_layout.addWidget(brightness_label)
        main_layout.addWidget(brightness_slider)

        main_layout.addWidget(sharpness_label)
        main_layout.addWidget(sharpness_slider)

        self.reset_sliders()
        self.setLayout(main_layout)

    def reset_sliders(self):
        self.sliders['brightness'].setValue(SLIDER_DEF_VAL)
        self.sliders['sharpness'].setValue(SLIDER_DEF_VAL)
        self.sliders['contrast'].setValue(SLIDER_DEF_VAL)

    @staticmethod
    def _get_converted_point(user_p1, user_p2, p1, p2, x):
        r = (x - user_p1) / (user_p2 - user_p1)
        return p1 + r * (p2 - p1)

    def __adjust(self, prop):
        logging.debug('on %s slider released' % prop)
        slider = self.sliders[prop]

        slider.setToolTip(str(slider.value()))

        factor = AdjustingTab._get_converted_point(SLIDER_MIN_VAL, SLIDER_MAX_VAL, BRIGHTNESS_FACTOR_MIN,
                                                   BRIGHTNESS_FACTOR_MAX, slider.value())
        logging.debug("%s factor: %f" % (prop, factor))

        global image_preview, drawer, operations
        operation = operations.get_operation(prop)
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, factor)
        self.parent.parent.refresh_image()

    def on_brightness_slider_released(self):
        self.__adjust('brightness')

    def on_contrast_slider_released(self):
        self.__adjust('contrast')

    def on_sharpness_slider_released(self):
        self.__adjust('sharpness')


class ModificationTab(QWidget):
    """Modification tab widget"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.width_label = QLabel('width:', self)
        self.width_label.setFixedWidth(100)

        self.height_label = QLabel('height:', self)
        self.height_label.setFixedWidth(100)

        self.width_box = QLineEdit(self)
        self.width_box.textEdited.connect(self.on_width_change)
        self.width_box.setMaximumWidth(100)

        self.height_box = QLineEdit(self)
        self.height_box.textEdited.connect(self.on_height_change)
        self.height_box.setMaximumWidth(100)

        self.unit_label = QLabel("px")
        self.unit_label.setMaximumWidth(50)

        self.apply_buttton = QPushButton("Apply")
        self.apply_buttton.setFixedWidth(90)
        self.apply_buttton.clicked.connect(self.on_apply)

        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_box)
        width_layout.addWidget(self.height_box)
        width_layout.addWidget(self.unit_label)

        apply_layout = QHBoxLayout()
        apply_layout.addWidget(self.apply_buttton)
        apply_layout.setAlignment(Qt.AlignRight)

        label_layout = QHBoxLayout()
        label_layout.setAlignment(Qt.AlignLeft)
        label_layout.addWidget(self.width_label)
        label_layout.addWidget(self.height_label)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(label_layout)
        main_layout.addLayout(width_layout)
        main_layout.addLayout(apply_layout)

        self.setLayout(main_layout)

    def set_boxes(self):
        global image_preview
        self.width_box.setText(str(image_preview.width))
        self.height_box.setText(str(image_preview.height))

    def on_height_change(self):
        logging.debug('on height change')

        try:
            h = int(self.height_box.text())
            self.apply_buttton.setEnabled(True)

            if(h < 0 or h > 1500):
                raise Exception()

            logging.debug('new height value: %d' % h)
        except:
            self.apply_buttton.setEnabled(False)
            logging.debug('invalid height value')

    def on_width_change(self):
        try:
            w = int(self.width_box.text())
            self.apply_buttton.setEnabled(True)

            if(w < 0 or w > 1500):
                raise Exception()

            logging.debug('new width value: %d' % w)
        except:
            self.apply_buttton.setEnabled(False)
            logging.debug('invalid width value')

    def on_apply(self):
        logging.debug('on apply')

        w = int(self.width_box.text())
        h = int(self.height_box.text())

        global image_preview, drawer, operations
        operation = operations.get_operation('resize')
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, (w, h))
        self.parent.parent.refresh_image()


class RotationTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        rotate_left_buttton = QPushButton("↺ 90°")
        rotate_left_buttton.clicked.connect(self.on_rotate_left)

        rotate_right_buttton = QPushButton("↻ 90°")
        rotate_right_buttton.clicked.connect(self.on_rotate_right)

        flip_left_buttton = QPushButton("⇆")
        flip_left_buttton.clicked.connect(self.on_flip_left)

        flip_top_buttton = QPushButton("↑↓")
        flip_top_buttton.clicked.connect(self.on_flip_top)

        rotate_label = QLabel("Rotate")
        rotate_label.setAlignment(Qt.AlignCenter)
        rotate_label.setFixedWidth(140)

        flip_label = QLabel("Flip")
        flip_label.setAlignment(Qt.AlignCenter)
        flip_label.setFixedWidth(140)

        label_layout = QHBoxLayout()
        label_layout.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(rotate_label)
        label_layout.addWidget(flip_label)

        buttton_layout = QHBoxLayout()
        buttton_layout.setAlignment(Qt.AlignCenter)
        buttton_layout.addWidget(rotate_left_buttton)
        buttton_layout.addWidget(rotate_right_buttton)
        buttton_layout.addWidget(flip_left_buttton)
        buttton_layout.addWidget(flip_top_buttton)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(label_layout)
        main_layout.addLayout(buttton_layout)

        self.setLayout(main_layout)

    def on_rotate_left(self):
        logging.debug('on rotate left')

        global image_preview, drawer, operations
        operation = operations.get_operation('rotate')
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, 90)
        self.parent.parent.refresh_image()
        self.parent.modification_tab.set_boxes()

    def on_rotate_right(self):
        logging.debug('on rotate right')

        global image_preview, drawer, operations
        operation = operations.get_operation('rotate')
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, 270)
        self.parent.parent.refresh_image()
        self.parent.modification_tab.set_boxes()

    def on_flip_left(self):
        logging.debug('on flip left')

        global image_preview, drawer, operations
        operation = operations.get_operation('flip')
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, Image.FLIP_LEFT_RIGHT)
        self.parent.parent.refresh_image()

    def on_flip_top(self):
        logging.debug('on flip top')

        global image_preview, drawer, operations
        operation = operations.get_operation('flip')
        drawer.set_operation(image_preview, operation)
        drawer.process(image_preview, Image.FLIP_TOP_BOTTOM)
        image_preview.set_display_strategy(strategies['label'])
        self.parent.parent.refresh_image()


class MainLayout(QVBoxLayout):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.file_name = None
        self._licensed = None

        self.upload_buttton = QPushButton("Upload")
        self.upload_buttton.clicked.connect(self.on_upload)

        self.reset_buttton = QPushButton("Reset")
        self.reset_buttton.setEnabled(False)
        self.reset_buttton.clicked.connect(self.on_reset)

        self.save_buttton = QPushButton("Save")
        self.save_buttton.setEnabled(False)
        self.save_buttton.clicked.connect(self.on_save)

        buttton_layout = QHBoxLayout()
        buttton_layout.setAlignment(Qt.AlignTop)
        buttton_layout.addWidget(self.upload_buttton)
        buttton_layout.addWidget(self.reset_buttton)
        buttton_layout.addWidget(self.save_buttton)
        self.addLayout(buttton_layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.addWidget(self.image_label)
        global strategies
        strategies['label'] = LabelStrategy(self)

        self.action_tabs = ActionTabs(self)
        self.addWidget(self.action_tabs)
        self.action_tabs.setVisible(False)

    def set_license(self, merchant, state):
        if (type(merchant) is not ProxyMainLayout):
            raise Exception

        self._licensed = state
        logging.debug('license set to %s', self._licensed)

    def on_upload(self):
        logging.debug('on upload buttton clicked')

        img_path, _ = QFileDialog.getOpenFileName(self.parent, "Open image",
                                                  "/home/traumgedanken/Pictures",
                                                  "Images (*.png *jpg)")
        self.file_name = ntpath.basename(img_path)

        global image_original, image_preview
        image_original = PediImage(img_path)
        image_preview = image_original.clone()
        self.refresh_image()

        self.reset_buttton.setEnabled(True)
        self.save_buttton.setEnabled(True)
        if (not self._licensed):
            self.save_buttton.setToolTip('Sign in to unlock this')
        self.action_tabs.setVisible(True)
        self.action_tabs.adjustment_tab.reset_sliders()
        self.action_tabs.modification_tab.set_boxes()

    def on_reset(self):
        logging.debug('on reset buttton clicked')

        global image_original, image_preview
        image_preview = image_original.clone()
        self.refresh_image()

    def on_save(self):
        logging.debug('on save buttton clicked')

        new_img_path = LicensedState.run(self)

        if new_img_path:
            logging.debug("save output image to %s" % new_img_path)
            global image_preview
            image_preview.save(new_img_path)

    def refresh_image(self):
        global image_preview, strategies
        image_preview.set_display_strategy(strategies['label'])
        image_preview.show()
        image_preview.set_display_strategy(strategies['thumb'])
        image_preview.show()
        self.action_tabs.modification_tab.set_boxes()


class ProxyMainLayout(MainLayout):
    def __init__(self, parent):
        super().__init__(parent)

        self.user_label = QPushButton()
        self.user_label.setStyleSheet(
            "QPushButton{font-size: 10px; color: grey;}")
        self.user_label.setFlat(True)
        self.user_label.clicked.connect(self.user_authorize)
        self.addWidget(self.user_label)
        
        self.user_authorize()

    def on_save(self):
        if (self._licensed):
            super().on_save()
        else:
            NotLicensedState.run(self)

    def user_authorize(self):
        user = None

        while(not user):
            login, ok_pressed = QInputDialog.getText(
                self.parent, "SIGN IN", "Enter your login:", QLineEdit.Normal, "")
            if (ok_pressed):
                user = DataBase.get_user(login)
            else:
                break

        self.user_label.setText(
            f'licenced to: {user.login}' if user else 'not licensed')
        self.set_license(self, bool(user))


class PediUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(600, 500)
        self.setMaximumSize(900, 900)
        self.setGeometry(600, 600, 600, 600)
        self.setWindowTitle('pedi OOP2')
        self.center()
        self.show()

        self.main_layout = ProxyMainLayout(self)
        self.setLayout(self.main_layout)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
