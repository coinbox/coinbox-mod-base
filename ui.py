import logging
logger = logging.getLogger(__name__)

import PySide
from PySide import QtCore, QtGui
import sys

import cbpos

class QtUIHandler(cbpos.BaseUIHandler):
    application = None
    __window = None
    __do_load = True
    
    @property
    def window(self):
        return self.__window
    
    @window.setter
    def window(self, val):
        self.__do_load = True
        self.__window = val
    
    @window.deleter
    def window(self):
        self.__window = None
        self.__do_load = False
    
    def init(self):
        logger.info('Platform: %s' % (sys.platform,))
        logger.info('PySide: %s' % (PySide.__version_info__,))
        
        logger.debug('Creating application instance...')
        self.application = QtGui.QApplication(sys.argv)
        return True
    
    def start(self):
        if not self.application:
            logger.critical('No QApplication set up.')
            return False
        
        if not self.__do_load:
            return False
        
        if self.__window is None:
            self.show_default()
        else:
            logger.debug('Main Window is not the default: ' + repr(self.__window))
            self.__window.show()
        return self.application.exec_()
    
    def show_default(self):
        logger.debug('Importing main window...')
        from .views.window import MainWindow
        
        self.window = MainWindow()
        
        logger.debug('Loading menu...')
        self.window.loadMenu()
        
        fullscreen = (cbpos.config['app', 'fullscreen'] != '')
        if fullscreen:
            self.window.showFullScreen()
        else:
            self.window.show()