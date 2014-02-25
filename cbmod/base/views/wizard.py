from PySide import QtGui, QtCore

from collections import defaultdict

import cbpos
logger = cbpos.get_logger(__name__)

class BaseWizard(QtGui.QWizard):
    pass

QWizardPageBaseType = type(QtGui.QWizardPage)

# class BaseWizardPageMeta(QWizardPageBaseType):
#     
#     def __new__(cls, clsname, bases, dct):
#         dct['pageId'] = cls.nextGeneratedId()
#         
#         logger.debug('BaseWizard {} has pageId of {}'.format(clsname, dct['pageId']))
#         
#         return super(BaseWizardPageMeta, cls).__new__(cls, clsname, bases, dct)
#     
#     generatedId = -1
#     
#     @classmethod
#     def nextGeneratedId(cls):
#         cls.generatedId += 1
#         return cls.generatedId

class BaseWizardPage(QtGui.QWizardPage):
#     __metaclass__ = BaseWizardPageMeta

    # Placeholder for the pageId which is assigned when adding pages dynamically
    pageId = None

class WizardPageCollection(object):
    PRIORITY_FIRST_HIGH = 0x00
    PRIORITY_FIRST_LOW = 0x0F
    PRIORITY_NONE = 0x88
    PRIORITY_LAST_LOW = 0xF0
    PRIORITY_LAST_HIGH = 0xFF
    
    pages = None
    priority = PRIORITY_NONE
    
    def handle_instances(self, pages):
        pass

class FirstTimeWizard(BaseWizard):
    
    def __init__(self, parent=None, flags=0):
        super(FirstTimeWizard, self).__init__(parent, flags)
        
        self.setWindowTitle(cbpos.tr.base_("Coinbox First-Time Setup Wizard"))
        
        self.finished.connect(self.onFinish)
        
        self.__first_page = BaseWizardPage(self)
        self.__first_page.pageId = self.addPage(self.__first_page)
        
        self.__first_page.setTitle("Say hi to the wizard")
        
        page_collections = defaultdict(list)
        for mod in cbpos.modules.all_loaders():
            try:
                collection = mod.first_run_wizard_pages()
            except AttributeError:
                continue
            except:
                raise
            else:
                page_collections[collection.priority].append(collection)
        
        for priority, collections in sorted(page_collections.iteritems()):
            for collection in collections:
                pages = []
                for page_cls in collection.pages:
                    page = page_cls(self)
                    page.pageId = self.addPage(page)
                    pages.append(page)
                collection.handle_instances(pages)
    
    def onFinish(self, result):
        if result == QtGui.QDialog.Accepted:
            cbpos.loader.load_database()
            cbpos.loader.load_interface()
            cbpos.loader.init_modules()
            cbpos.ui.show_next()
