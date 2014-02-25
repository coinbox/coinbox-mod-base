from pydispatch import dispatcher
from PySide import QtCore, QtGui

import cbpos
logger = cbpos.get_logger(__name__)

from .page import BasePage

class MainWindow(QtGui.QMainWindow):
    __inits = []
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabsClosable(False)
        self.tabs.setIconSize(QtCore.QSize(32, 32))
        self.tabs.currentChanged.connect(self.onCurrentTabChanged)
        
        self.toolbar = self.addToolBar('Base')
        self.toolbar.setIconSize(QtCore.QSize(48,48)) #Suitable for touchscreens
        self.toolbar.setObjectName('BaseToolbar')
        
        toolbarStyle = cbpos.config['menu', 'toolbar_style']
        # The index in this list is the same as that in the configuration page
        available_styles = (
              QtCore.Qt.ToolButtonFollowStyle,
              QtCore.Qt.ToolButtonIconOnly,
              QtCore.Qt.ToolButtonTextOnly,
              QtCore.Qt.ToolButtonTextBesideIcon,
              QtCore.Qt.ToolButtonTextUnderIcon,
              )
        try:
            toolbarStyle = available_styles[int(toolbarStyle)]
        except (ValueError, TypeError, IndexError):
            toolbarStyle = QtCore.Qt.ToolButtonFollowStyle
        self.toolbar.setToolButtonStyle(toolbarStyle)
        
        self.setCentralWidget(self.tabs)
        
        self.statusBar().showMessage(cbpos.tr._('Coinbox POS is ready.'))
        
        self.setWindowTitle('Coinbox')
        
        self.callInit()
        
        self.loadToolbar()
        self.loadMenu()
    
    def loadToolbar(self):
        """
        Loads the toolbar actions, restore toolbar state, and restore window geometry.
        """

        mwState = cbpos.config['mainwindow', 'state']
        mwGeom  = cbpos.config['mainwindow', 'geometry']

        for act in cbpos.menu.actions:
            # TODO: Remember to load an icon with a proper size (eg 48x48 px for touchscreens)
            action = QtGui.QAction(QtGui.QIcon(act.icon), act.label, self)
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
    
    def loadMenu(self):
        """
        Load the menu root items and items into the QTabWidget with the appropriate pages. 
        """
        show_empty_root_items = cbpos.config['menu', 'show_empty_root_items']
        show_disabled_items = cbpos.config['menu', 'show_disabled_items']
        hide_tab_bar = not cbpos.config['menu', 'show_tab_bar']
        
        if hide_tab_bar:
            # Hide the tab bar and prepare the toolbar for extra QAction's
            self.tabs.tabBar().hide()
            # This pre-supposes that the menu items will come after the actions
            self.toolbar.addSeparator()
        
        for root in cbpos.menu.items:
            if not root.enabled and not show_disabled_items:
                continue
            
            if show_disabled_items:
                # Show all child items
                children = root.children
            else:
                # Filter out those which are disabled
                children = [i for i in root.children if i.enabled]
            
            # Hide empty menu root items
            if len(children) == 0 and not show_empty_root_items:
                continue
            
            # Add the tab
            widget = self.getTabWidget(children)
            icon = QtGui.QIcon(root.icon)
            index = self.tabs.addTab(widget, icon, root.label)
            widget.setEnabled(root.enabled)
            
            # Add the toolbar action if enabled
            if hide_tab_bar:
                # TODO: Remember to load an icon with a proper size (eg 48x48 px for touchscreens)
                action = QtGui.QAction(QtGui.QIcon(icon), root.label, self)
                action.onTrigger = lambda n=index: self.tabs.setCurrentIndex(n)
                action.triggered.connect(action.onTrigger)
                self.toolbar.addAction(action)

    def onCurrentTabChanged(self, index, tabs=None):
        if tabs is None:
            tabs = self.tabs
        widget = tabs.widget(index)
        try:
            signal = widget.shown
        except AttributeError:
            pass
        else:
            signal.emit()

    def getTabWidget(self, items):
        """
        Returns the appropriate window to be placed in the main QTabWidget,
        depending on the number of children of a root menu item.
        """
        count = len(items)
        if count == 0:
            # If there are no child items, just return an empty widget
            widget = QtGui.QWidget()
            widget.setEnabled(False)
            return widget
        elif count == 1:
            # If there is only one item, show it as is.
            logger.debug('Loading menu page for %s', items[0].name)
            widget = items[0].page()
            widget.setEnabled(items[0].enabled)
            return widget
        else:
            # If there are many children, add them in a QTabWidget
            tabs = QtGui.QTabWidget()
            tabs.currentChanged.connect(lambda i, t=tabs: self.onCurrentTabChanged(i, t))

            for item in items:
                logger.debug('Loading menu page for %s', item.name)
                
                widget = item.page()
                icon = QtGui.QIcon(item.icon)
                tabs.addTab(widget, icon, item.label)
                widget.setEnabled(item.enabled)
            return tabs
    
    def saveWindowState(self):
        """
        Saves the main window state (position, size, toolbar positions)
        """
        mwState = self.saveState().toBase64() 
        mwGeom  = self.saveGeometry().toBase64() 
        cbpos.config['mainwindow', 'state'] = unicode(mwState)
        cbpos.config['mainwindow', 'geometry'] = unicode(mwGeom)
        cbpos.config.save()


    def closeEvent(self, event):
        """
        Perform necessary operations before closing the window.
        """
        self.saveWindowState()
        #do any other thing before closing...
        event.accept()
    
    @classmethod
    def addInit(cls, init):
        """
        Adds the `init` method to the list of extensions of the `MainWindow.__init__`.
        """
        cls.__inits.append(init)
    
    def callInit(self):
        """
        Handle calls to `__init__` methods of extensions of the MainWindow.
        """
        for init in self.__inits:
            init(self)
