import logging
logger = logging.getLogger(__name__)

from PySide import QtCore, QtGui

import cbpos

from pydispatch import dispatcher

class MainWindow(QtGui.QMainWindow):
    __inits = []
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabsClosable(False)
        self.tabs.setIconSize(QtCore.QSize(32, 32))
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().hide()
        
        self.setCentralWidget(self.tabs)
        
        self.statusBar().showMessage(cbpos.tr._('Coinbox POS is ready.'))
        
        self.setWindowTitle('Coinbox')
        
        self.callInit()
    
    @staticmethod
    def addInit(init):
        MainWindow.__inits.append(init)
    
    def callInit(self):
        logger.debug('There are (%d) extensions to the MainWindow' % (len(self.__inits),))
        for init in self.__inits:
            init(self)
    
    def loadToolbar(self):
        """
        Loads the toolbar actions, restore toolbar state, and restore window geometry.
        """

        mwState = cbpos.config['mainwindow', 'state']
        mwGeom  = cbpos.config['mainwindow', 'geometry']

        self.toolbar = self.addToolBar('Base')
        self.toolbar.setIconSize(QtCore.QSize(48,48)) #Suitable for touchscreens
        self.toolbar.setObjectName('BaseToolbar')

        for act in cbpos.menu.actions:
            action = QtGui.QAction(QtGui.QIcon(act.icon), act.label, self) # TODO: Remember to load an icon with a proper size (eg 48x48 px for touchscreens)
            action.setShortcut(act.shortcut)
            action.triggered.connect(act.trigger)
            self.toolbar.addAction(action)


        #Restores the saved mainwindow's toolbars and docks, and then the window geometry.
        if mwState is not None:
            self.restoreState( QtCore.QByteArray.fromBase64(mwState) )
        if mwGeom is not None:
            self.restoreGeometry( QtCore.QByteArray.fromBase64(mwGeom) )
        else:
            self.setGeometry(0, 0, 800, 600)


    def saveWindowState(self):
        """
        Saves the main window state (position, size, toolbar positions)
        """
        mwState = self.saveState().toBase64() 
        mwGeom  = self.saveGeometry().toBase64() 
        cbpos.config['mainwindow', 'state'] = '%s'%mwState #why i need to do this? it is supposed that toBase64() returns a string.
        cbpos.config['mainwindow', 'geometry'] = '%s'%mwGeom
        cbpos.config.save()


    def closeEvent(self, event):
        self.saveWindowState()
        #do any other thing before closing...
        event.accept()
    
    def loadMenu(self):
        """
        Load the menu root items and items into the tab widget with the appropriate pages. 
        """
        show_empty_root_items = cbpos.config['menu', 'show_empty_root_items']
        show_disabled_items = cbpos.config['menu', 'show_disabled_items']
        
        self.toolbar.addSeparator()
        
        for root in cbpos.menu.items:
            if not root.enabled and not show_disabled_items:
                continue
            
            if show_disabled_items:
                children = root.children
            else:
                children = [i for i in root.children if i.enabled]
            
            # Hide empty menu root items
            if len(children) == 0 and not show_empty_root_items:
                continue
            
            widget = self.getTabWidget(children)
            icon = QtGui.QIcon(root.icon)
            i = self.tabs.addTab(widget, icon, root.label)
            widget.setEnabled(root.enabled)
            
            action = QtGui.QAction(QtGui.QIcon(icon), root.label, self) # TODO: Remember to load an icon with a proper size (eg 48x48 px for touchscreens)
            action.onTrigger = lambda n=i: self.onTrigger(n)
            action.triggered.connect(action.onTrigger)
            self.toolbar.addAction(action)

    def onTrigger(self, i):
        print i
        self.tabs.setCurrentIndex(i)

    def getTabWidget(self, items):
        """
        Returns the appropriate widget to be placed in the main tabWidget,
        depending on the number of children of a root menu item.
        """
        count = len(items)
        if count == 0:
            widget = QtGui.QWidget()
            widget.setEnabled(False)
            return widget
        elif count == 1:
            logger.debug('Loading menu page for %s' % (items[0].name,))
            widget = items[0].page()
            widget.setEnabled(items[0].enabled)
            return widget
        else:
            tabs = QtGui.QTabWidget()

            for item in items:
                logger.debug('Loading menu page for %s' % (item.name,))
                
                widget = item.page()
                icon = QtGui.QIcon(item.icon)
                tabs.addTab(widget, icon, item.label)
                widget.setEnabled(item.enabled)
            return tabs
