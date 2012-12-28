import logging
logger = logging.getLogger(__name__)

from PySide import QtCore, QtGui

import cbpos
from cbpos.mod.auth.views.dialogs.clockingpanel import ClockingPanel

from pydispatch import dispatcher

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.tabs = QtGui.QTabWidget(self)
        self.tabs.setTabsClosable(False)
        self.tabs.setIconSize(QtCore.QSize(32, 32))
        self.tabs.setDocumentMode(True)
        
        self.setCentralWidget(self.tabs)
        
        self.statusBar().showMessage(cbpos.tr._('Coinbox POS is ready.'))
        
        #self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Coinbox')

        #adds the clock-in/clock-out slide panel.
        self.clockingPanel = ClockingPanel(self, cbpos.res.auth("images/clocking.svg"))
        self.clockingPanel.setSize(300, 260)
        self.clockingPanel.btnLogin.clicked.connect(self.onDoClocking)
        self.clockingPanel.btnExit.clicked.connect(self.do_hidePanel)
        self.clockingPanel.editUsername.currentIndexChanged.connect(self.clockingPanel.editPassword.setFocus)
        self.clockingPanel.editPassword.returnPressed.connect(self.onDoClocking)
        dispatcher.connect(self.do_show_clocking, signal='do-show-clockin-panel', sender=dispatcher.Any)
        dispatcher.connect(self.do_show_clocking, signal='do-show-clockout-panel', sender=dispatcher.Any)
        dispatcher.connect(self.onAuthError, signal='do-show-error-on-clock-in', sender=dispatcher.Any)
        dispatcher.connect(self.onClockingDone, signal='do-hide-clockin-panel', sender=dispatcher.Any)

    def do_show_clocking(self, sender, isIn):
        self.clockingPanel.setIsIn(isIn)
        self.clockingPanel.showPanel()

    def do_hidePanel(self):
        self.clockingPanel.clean()
        self.clockingPanel.hidePanel()

    def onDoClocking(self):
        username = self.clockingPanel.getUserName()
        password = self.clockingPanel.getPassword()
        dispatcher.send(signal='do-clocking', sender='base-mod', usern=username, passw=password, isIn=self.clockingPanel.isIn() )
        self.clockingPanel.clean()

    def onAuthError(self, sender, msg):
        self.clockingPanel.setError(msg)

    def onClockingDone(self, sender, msg):
        self.clockingPanel.setError(msg)
        #Wait 3 seconds to close the panel.
        QtCore.QTimer.singleShot(3000, self.clockingPanel.hidePanel)
        
    def loadToolbar(self):
        """
        Loads the toolbar actions, restore toolbar state, and restore window geometry.
        """
        from cbpos import _actions #The actions list that holds all the actions for the toolbar.

        action = QtGui.QAction(QtGui.QIcon(cbpos.res.base("images/cancel.png")), 'Exit', self)
        action.setShortcut('Ctrl+Q')
        action.triggered.connect(self.close)

        mwState = cbpos.config['mainwindow', 'state']
        mwGeom  = cbpos.config['mainwindow', 'geometry']

        self.toolbar = self.addToolBar('Base')
        self.toolbar.setIconSize(QtCore.QSize(48,48)) #Suitable for touchscreens
        self.toolbar.setObjectName('BaseToolbar')
        self.toolbar.addAction(action)

        for act in _actions:
            action = QtGui.QAction(QtGui.QIcon(act['icon']), act['label'], self) #Remember to load an icon with a proper size (eg 48x48 px for touchscreens)
            action.setShortcut(act['shortcut'])
            action.triggered.connect(act['callback'])
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
        Load the menu "root" items and "items" into the toolbook with the appropriate pages. 
        """
        show_empty_root_items = cbpos.config['menu', 'show_empty_root_items']
        show_disabled_items = cbpos.config['menu', 'show_disabled_items']
        
        for root in cbpos.menu.main.items:
            if not root.enabled and not show_disabled_items:
                continue
            enabled_children = [i for i in root.children if i.enabled]
            if show_disabled_items:
                children = root.children
            else:
                children = enabled_children
            # Hide empty menu root items
            if len(children) == 0 and not show_empty_root_items:
                continue
            widget = self.getTabWidget(children)
            icon = QtGui.QIcon(root.image)
            self.tabs.addTab(widget, icon, root.label)
            widget.setEnabled(root.enabled)# and len(enabled_children) != 0)

    def getTabWidget(self, items):
        """
        Returns the appropriate window to be placed in the main Toolbook depending on the items of a root menu item.
        """
        count = len(items)
        if count == 0:
            widget = QtGui.QWidget()
            widget.setEnabled(False)
            return widget
        elif count == 1:
            widget = items[0].page()
            widget.setEnabled(items[0].enabled)
            return widget
        else:
            tabs = QtGui.QTabWidget()

            for item in items:
                logger.debug('Loading menu for %s' % (item.label,))
                widget = item.page()
                icon = QtGui.QIcon(item.image)
                tabs.addTab(widget, icon, item.label)
                widget.setEnabled(item.enabled)
            return tabs
