from PySide import QtCore, QtGui

import cbpos

from cbpos.mod.base.controllers import ValidationError

class FormPage(QtGui.QWidget):
    controller = None
    
    def __init__(self):
        super(FormPage, self).__init__()

        self.editing = False

        self.list = QtGui.QListView()
        self.list.activated.connect(self.onItemActivated)
        
        buttonBox = QtGui.QDialogButtonBox()
        
        
        self.deleteBtn = buttonBox.addButton("Delete", QtGui.QDialogButtonBox.DestructiveRole)
        self.deleteBtn.pressed.connect(self.onDeleteButton)
        
        self.newBtn = buttonBox.addButton("New", QtGui.QDialogButtonBox.ActionRole)
        self.newBtn.pressed.connect(self.onNewButton)
        
        self.editBtn = buttonBox.addButton("Edit", QtGui.QDialogButtonBox.ActionRole)
        self.editBtn.pressed.connect(self.onEditButton)
        
        self.okBtn = buttonBox.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.okBtn.pressed.connect(self.onOkButton)
        
        self.cancelBtn = buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        self.cancelBtn.pressed.connect(self.onCancelButton)
        
        fields = self.controller.fields()
        widgets = self.widgets()
        
        rows = []
        self.f = dict()
        self.defaults = dict()
        for field in widgets:
            f, widget = field
            label, default = fields.get(f, ["", None]) 
            self.f[f] = widget
            self.defaults[f] = default
            rows.append((label, widget))
        
        self.formContainer = QtGui.QWidget()
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        [form.addRow(*row) for row in rows]
        
        self.formContainer.setLayout(form)
        self.formContainer.setEnabled(False)
        
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.formContainer)
        
        formLayout = QtGui.QVBoxLayout()
        formLayout.setSpacing(10)
        formLayout.addWidget(self.scrollArea)
        formLayout.addWidget(buttonBox)
        
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(10)
        
        if self.controller.single:
            self.newBtn.hide()
            self.deleteBtn.hide()
        else:
            layout.addWidget(self.list)
        layout.addLayout(formLayout)
        
        self.setLayout(layout)
        
        self.populate()
    
    def populate(self):
        self.editing = False
        self.formContainer.setEnabled(False)
        if self.controller.single:
            self.setItem(self.controller.item())
        else:
            model = SimpleList([(i.display, i) for i in self.controller.items()])
            self.list.setModel(model)
            self.setItem(None)
    
    def setItem(self, item=None):
        self.item = item
        if item is None:
            for f in self.f:
                self.setDataOnControl(f, self.defaults[f])
            self.deleteBtn.setEnabled(False)
            self.editBtn.setEnabled(False)
        else:
            for f in self.f:
                self.setDataOnControl(f, self.controller.getDataFromItem(f, item))
            self.deleteBtn.setEnabled(not self.editing and self.controller.canDeleteItem(item))
            self.editBtn.setEnabled(not self.editing and self.controller.canEditItem(item))
        self.newBtn.setEnabled(not self.editing and self.controller.canAddItem())
        self.okBtn.setEnabled(self.editing)
        self.cancelBtn.setEnabled(self.editing)
        self.list.setEnabled(not self.editing)
    
    def onItemActivated(self, index):
        self.editing = False
        item = self.list.model().contents[index.row()][1]
        self.setItem(item)
    
    def onOkButton(self):
        # TODO: validation
        try:
            data = {}
            for f in self.f:
                k, v = self.getDataFromControl(f)
                if k is None:
                    continue
                data[k] = v
            if self.item is None:
                self.controller.new(data)
            else:
                self.controller.update(self.item, data)
        except ValidationError as e:
            QtGui.QMessageBox.information(self, 'Form', unicode(e), QtGui.QMessageBox.Ok)
            return
        self.populate()
    
    def onEditButton(self):
        self.editing = True
        self.formContainer.setEnabled(True)
        self.setItem(self.item)
    
    def onCancelButton(self):
        self.editing = False
        self.setItem(self.item)
        self.formContainer.setEnabled(False)
    
    def onDeleteButton(self):
        if self.item is not None:
            self.controller.delete(self.item)
            self.populate()
    
    def onNewButton(self):
        self.editing = True
        self.setItem(None)
        self.formContainer.setEnabled(True)
    
    def widgets(self):
        return tuple()
    
    def getDataFromControl(self, field):
        return (None, None)
    
    def setDataOnControl(self, field, data):
        pass

class SimpleList(QtCore.QAbstractListModel):
    def __init__(self, contents):
        super(SimpleList, self).__init__()
        self.contents = contents

    def rowCount(self, parent):
        return len(self.contents)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return unicode(self.contents[index.row()][0])
