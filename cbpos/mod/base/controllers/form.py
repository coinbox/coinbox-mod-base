from PySide import QtCore, QtGui

import cbpos

class FormController(object):
    cls = None
    single = False
    
    def new(self, data=dict()):
        item = self.cls()
        session = cbpos.database.session()
        session.add(item)
        item.update(**data)
    
    def delete(self, item):
        item.delete()
    
    def update(self, item, data=dict()):
        item.update(**data)
    
    def fields(self):
        return {}
    
    def item(self):
        return None
    
    def items(self):
        return []
    
    def canDeleteItem(self, item):
        return True
    
    def canEditItem(self, item):
        return True
    
    def canAddItem(self):
        return True
    
    def getDataFromItem(self, field, item):
        return None

class ValidationError(ValueError):
    pass
