from PySide import QtCore, QtGui

import cbpos
logger = cbpos.get_logger(__name__)

class ImagePicker(QtGui.QPushButton):
    
    __image = None
    __path = None
    
    def __init__(self):
        super(ImagePicker, self).__init__()
        
        self.pressed.connect(self.onPress)
        
        self.updateText()
    
    def onPress(self):
        (path, filter) = QtGui.QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg)")
        self.setPath(path)
    
    def updateText(self):
        if self.__image or self.__path:
            self.setText("Change")
        else:
            self.setText("Set Image")
    
    def setImage(self, image):
        self.__image = image
        self.__path = None
        
        self.updateText()
    
    def setPath(self, path):
        self.__image = None
        self.__path = path
        
        self.updateText()
    
    def image(self):
        return self.__image
    
    def image_path(self):
        return self.__path
