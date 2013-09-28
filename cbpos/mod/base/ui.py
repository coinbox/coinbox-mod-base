import PySide
from PySide import QtCore, QtGui
import sys

import cbpos
logger = cbpos.get_logger(__name__)

class QtUIHandler(cbpos.BaseUIHandler):
    application = None
    extensions = None
    __window = None
    __do_load = True
    
    def __init__(self):
        self.extensions = []
    
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
        
        from cbpos.mod.base.views import MainWindow as BaseMainWindow
        if len(self.extensions) > 0:
            exts = tuple(self.extensions + [BaseMainWindow])
            MainWindow = type('ExtendedMainWindow', exts, {})
            
            logger.debug('Extensions (%d): %s',
                         len(exts)-1,
                         ', '.join(e.__name__ for e in exts[:-1]))
            
            for ext in self.extensions:
                try:
                    init = ext.init
                except AttributeError:
                    pass
                else:
                    MainWindow.addInit(init)
                    del ext.init
        else:
            MainWindow = BaseMainWindow
            
            logger.debug('No extensions.')
        
        logger.debug('Loading main window %s...', MainWindow.__name__)
        self.window = MainWindow()
        
        fullscreen = bool(cbpos.config['app', 'fullscreen'])
        if fullscreen:
            self.window.showFullScreen()
        else:
            self.window.showNormal()
    
    def extend_default(self, extension):
        self.extensions.append(extension)

class MainWindowExtension(object):
    pass
