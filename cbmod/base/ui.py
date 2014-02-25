import PySide
from PySide import QtCore, QtGui
import sys
from collections import defaultdict

import cbpos
logger = cbpos.get_logger(__name__)

class QtUIHandler(cbpos.BaseUIHandler):
    application = None
    extensions = None
    __started = False
    __window = None
    __wizard = None
    __do_load = True
    __current_window = None
    
    PRIORITY_MIN = 0x00
    
    PRIORITY_FIRST_HIGHEST = 0x0F
    
    PRIORITY_FIRST_HIGH = 0x60
    PRIORITY_FIRST_MEDIUM = 0x67
    PRIORITY_FIRST_LOW = 0x6F
    
    PRIORITY_FIRST = 0x6F
    PRIORITY_NONE = 0x70
    PRIORITY_LAST = 0x80
    
    PRIORITY_LAST_LOW = 0x80
    PRIORITY_LAST_MEDIUM = 0x87
    PRIORITY_LAST_HIGH = 0x8F
    
    PRIORITY_LAST_HIGHEST = 0xF0
    
    PRIORITY_MAX = 0xFF
    
    def __init__(self):
        self.extensions = []
        self.__window_chain = defaultdict(list)
    
    @property
    def load(self):
        return self.__do_load
    
    @load.setter
    def load(self, val):
        self.__do_load = bool(val)
    
    def set_main_window(self, win):
        logger.debug("Setting main window to %s", win)
        self.__window = win
        return self.__window
    
    def replace_window(self, win):
        logger.debug("Replacing window with %s", win)
        if not self.__started:
            raise ValueError("Application not started. Cannot replace window.")
        
        self.__window.close()
        
        return self.__show_window(win)
    
    def chain_window(self, win, priority=PRIORITY_NONE):
        logger.debug("Chaining window %s with priority %s", win, priority)
        if not (self.PRIORITY_MIN <= priority <= self.PRIORITY_MAX):
            raise ValueError("Invalid priority value {}".format(priority))
        
        if self.__started:
            raise ValueError("Application already started cannot chain window")
        
        self.__window_chain[priority].append(win)
        return win

    def show_next(self):
        logger.debug("Showing next window...")
        try:
            win = self.windows.next()
        except StopIteration:
            logger.debug("The next window is the main window")
            return self.__show_main_window()
        else:
            logger.debug("The next window is %s", win)
            return self.__show_window(win)
    
    @property
    def windows(self):
        """
        An iterator over the chained windows, ordered by priority.
        """
        for p in sorted(self.__window_chain.iterkeys()):
            try:
                win = self.__window_chain[p].pop(0)
            except IndexError:
                del self.__window_chain[p]
                continue
            else:
                yield win
    
    def extend_default_main_window(self, extension):
        self.extensions.append(extension)
    
    def init(self):
        logger.info('Platform: %s' % (sys.platform,))
        logger.info('PySide: %s' % (PySide.__version_info__,))
        
        logger.debug('Creating application instance...')
        self.application = QtGui.QApplication(sys.argv)
        return True
    
    def handle_first_run(self):
        assert cbpos.first_run, 'Cannot handle first run if not actually first-run'
        
        cbpos.loader.autoload_database(False)
        cbpos.loader.autoload_interface(False)
    
    def start(self):
        if self.application is None:
            logger.critical('No QApplication set up.')
            return False
        
        if not self.__do_load:
            logger.debug('Will not load the window.')
            return False
        
        if cbpos.first_run:
            logger.info("Follow me, I'll get you to the wizard.")
            from cbmod.base.views import FirstTimeWizard
            self.__wizard = FirstTimeWizard()
            self.chain_window(self.__wizard, self.PRIORITY_FIRST_HIGHEST)
        
        self.__started = True
        self.show_next()
        
        return self.application.exec_()
    
    def __load_default_main_window(self):
        logger.debug('Importing main window...')
        from cbmod.base.views import MainWindow as BaseMainWindow
        
        if len(self.extensions) > 0:
            logger.debug('Loading main window extensions...')
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
            #del MainWindow.init
        else:
            logger.debug('No extensions.')
            MainWindow = BaseMainWindow
        
        logger.debug('Loading main window %s...', MainWindow.__name__)
        self.__window = MainWindow()
    
    def __show_main_window(self):
        if self.__window is None:
            self.__load_default_main_window()
        else:
            logger.debug('Main Window is not the default: ' + repr(self.__window))
        
        return self.__show_window(self.__window)
    
    def __show_window(self, win):
        """
        Show the window properly.
        Hold on to a reference to the window so that it does not get garbage
        collected.
        Handles the fullscreen configuration too.
        """
        self.__current_window = win
        # Decide whether to show the window in fullscreen or not
        fullscreen = bool(cbpos.config['app', 'fullscreen'])
        if fullscreen:
            win.showFullScreen()
        else:
            win.showNormal()
        
        return self.__current_window

class MainWindowExtension(object):
    pass
