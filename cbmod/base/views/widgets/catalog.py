from PySide import QtGui, QtCore

import cbpos

PARENT, CHILD, UP, ALL = 0, 1, 2, 3
ITEM, TYPE = QtCore.Qt.UserRole+1, QtCore.Qt.UserRole+2

class Catalog(QtGui.QWidget):
    
    childSelected = QtCore.Signal('QVariant')
    parentSelected = QtCore.Signal('QVariant')
    searchChanged = QtCore.Signal(str)
    
    def __init__(self):
        super(Catalog, self).__init__()
        self.search = QtGui.QLineEdit()
        self.search.setPlaceholderText(cbpos.tr.base_('Search'))
        
        self.search.textChanged.connect(self.onSearchTextChanged)
        self.search.returnPressed.connect(self.onSearchReturnPressed)
        
        icon = QtGui.QIcon.fromTheme('edit-clear')
        
        if icon.isNull():
            self.clearBtn = QtGui.QPushButton(cbpos.tr.base_('Clear'))
        else:
            self.clearBtn = QtGui.QPushButton()
            self.clearBtn.setIcon(icon)
        self.clearBtn.pressed.connect(self.onSearchClear)
        
        self.list = QtGui.QListWidget()
        self.list.setViewMode(QtGui.QListWidget.IconMode)
        self.list.itemActivated.connect(self.onListItemActivated)
        self.list.setIconSize(QtCore.QSize(128, 128))
        
        top = QtGui.QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(self.clearBtn)
        
        layout = QtGui.QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.list)
        self.setLayout(layout)
        
        self.icons = {UP: QtGui.QIcon.fromTheme('go-up'),
                      CHILD: QtGui.QIcon.fromTheme('text-x-generic'),
                      PARENT: QtGui.QIcon.fromTheme('folder'),
                      ALL: QtGui.QIcon.fromTheme('package-x-generic')}
        
        self.show_all = True
        self.in_all = False
        
        self.__current = None
        self.__tree = []
        self.__display = [[], []]

    def populate(self, parent=None, search=None, show_all=False):
        self.__current = parent
        self.__search = search
        self.in_all = show_all
        
        if self.in_all or (parent is None and search is not None):
            parents, children = [], self.getAll(search=search)
        else:
            parents, children = self.getChildren(parent=parent, search=search)
        
        # If iterators are used (i.e. Query objects), they cannot be
        # iterated over more than once. So we need to convert them to lists.
        parents, children = list(parents), list(children)
        
        self.list.clear()
        
        if search is None:
            if parent is not None or self.in_all:
                self.addItem("[Up]", None, None, UP)
            elif self.show_all:
                self.addItem("[All]", None, None, ALL)
        
        for data in parents:
            try:
                item, image = data
            except (TypeError, ValueError):
                item = data
                image = None
            self.addItem(item.display, image, item, PARENT)
        
        for data in children:
            try:
                item, image = data
            except (TypeError, ValueError):
                item = data
                image = None
            self.addItem(item.display, image, item, CHILD)
        
        self.__display = [parents, children]

    def addItem(self, label, image, data, t):
        item = QtGui.QListWidgetItem(label)
        item.setData(ITEM, data)
        item.setData(TYPE, t)
        if image:
            icon = QtGui.QIcon(image)
            item.setIcon(icon)
        else:
            item.setIcon(self.icons[t])
        return self.list.addItem(item)

    def onSearchTextChanged(self):
        QtCore.QTimer.singleShot(200, lambda s=self.search.text(): self.checkSearch(s))
    
    def checkSearch(self, last):
        if last == self.search.text():
            self.doSearch()
    
    def onSearchReturnPressed(self):
        self.doSearch()
        
        parents, children = self.__display
        if len(parents) == 0 and len(children) == 1:
            data, label = children[0]
            self.childSelected.emit(data)
        elif len(parents) == 1 and len(children) == 0:
            data, label = parents[0]
            self.parentSelected.emit(data)
    
    def onSearchClear(self):
        self.search.setText('')
        self.doSearch()
    
    def doSearch(self):
        s = self.search.text()
        if s == '':
            s = None
        self.populate(parent=self.__current, search=s)
        self.searchChanged.emit(self.__search)

    def onListItemActivated(self):
        item = self.list.currentItem()
        data, t = item.data(ITEM), item.data(TYPE)
        if t == PARENT:
            self.__tree.append(self.__current)
            self.populate(parent=data, search=self.__search)
            self.parentSelected.emit(data)
        elif t == CHILD:
            self.childSelected.emit(data)
        elif t == UP:
            if self.in_all:
                parent = None
            else:
                parent = self.__tree.pop()
            self.populate(parent=parent, search=self.__search)
        elif t == ALL:
            self.populate(parent=None, search=None, show_all=True)

    def getAll(self, search=None):
        raise NotImplementedError, "getAll is not defined"
    def getChildren(self, parent=None, search=None):
        raise NotImplementedError, "getChildren is not defined"
