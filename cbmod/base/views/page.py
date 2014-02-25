from PySide import QtCore, QtGui

import cbpos

class BasePage(QtGui.QWidget):
    shown = QtCore.Signal()
    __shown_before = False
    
    def __init__(self, parent=None, flags=0):
        super(BasePage, self).__init__(parent, flags)
        
        self.shown.connect(self.__onShown)
        self.__shown_before = False
    
    def __onShown(self):
        if not self.__shown_before:
            self.populate()
            self.__shown_before = True
    
    def populate(self):
        pass
