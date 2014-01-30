from pydispatch import dispatcher

import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    def load_models(self):
        from cbmod.base.models import StoredFile
        return [StoredFile]

    def init(self):
        from cbmod.base.controllers import printing
        
        printing.manager = printing.PrinterManager()
        
        dispatcher.connect(cbpos.terminate, signal='exit', sender=dispatcher.Any)
        dispatcher.connect(printing.manager.register_function, signal='printing-register-function', sender=dispatcher.Any)
        dispatcher.connect(printing.manager.handle, signal='printing-handle', sender=dispatcher.Any)
        
        return True

    def ui_handler(self):
        from cbmod.base.ui import QtUIHandler
        return QtUIHandler()

    def menu(self):
        from cbpos.interface import MenuRoot
        return [
                [MenuRoot('main',
                            label=cbpos.tr.base_('Main'),
                            icon=cbpos.res.base('images/menu-main.png'),
                            rel=0,
                            priority=5
                          ),
                 MenuRoot('system',
                            label=cbpos.tr.base_('System'),
                            icon=cbpos.res.base('images/menu-system.png'),
                            rel=-1,
                            priority=4
                          ),
                 MenuRoot('administration',
                            label=cbpos.tr.base_('Administration'),
                            icon=cbpos.res.base('images/menu-administration.png'),
                            rel=-1,
                            priority=5
                          )
                 ],
                []
                ]
    
    def actions(self):
        from cbpos.interface import Action
        return [Action('quit',
                       label=cbpos.tr.base_('Exit'),
                       icon=cbpos.res.base("images/cancel.png"),
                       shortcut='Ctrl+Q',
                       signal='exit'
                       )
                ]

    def config_pages(self):
        from cbmod.base.views import MenuConfigPage, AppConfigPage, LocaleConfigPage, PrintingConfigPage
        return [AppConfigPage, MenuConfigPage, LocaleConfigPage, PrintingConfigPage]
