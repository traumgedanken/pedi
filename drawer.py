class Drawer:
    def set_operation(self, pedi_image, operation):
        pedi_image.operation = operation

    def process(self, pedi_image, option):
        pedi_image.redraw(option)
