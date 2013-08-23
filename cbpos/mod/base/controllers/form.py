from PySide import QtCore, QtGui

import cbpos
logger = cbpos.get_logger(__name__)

class FormController(object):
    cls = None
    single = False
    
    def new(self, data=dict()):
        item = self.cls()
        if not item.update(**data):
            raise ValidationError("Something went wrong")
    
    def delete(self, item):
        if not item.delete():
            raise ValidationError("Something went wrong")
    
    def update(self, item, data=dict()):
        if not item.update(**data):
            raise ValidationError("Something went wrong")
    
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
