from pydispatch import dispatcher

import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    name = 'Base Module'
    config = [['mod.menu', {'show_tab_bar': '', 'toolbar_style': '0'}]]

    def init(self):
        dispatcher.connect(cbpos.terminate, signal='exit', sender=dispatcher.Any)
        
        return True

    def ui_handler(self):
        from cbpos.mod.base.ui import QtUIHandler
        return QtUIHandler()

    def menu(self):
        from cbpos.interface import MenuRoot
        return [
                [MenuRoot('main',
                            label=cbpos.tr.base._('Main'),
                            icon=cbpos.res.base('images/menu-main.png'),
                            rel=0,
                            priority=5
                          ),
                 MenuRoot('system',
                            label=cbpos.tr.base._('System'),
                            icon=cbpos.res.base('images/menu-system.png'),
                            rel=-1,
                            priority=4
                          ),
                 MenuRoot('administration',
                            label=cbpos.tr.base._('Administration'),
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
                       label=cbpos.tr.base._('Exit'),
                       icon=cbpos.res.base("images/cancel.png"),
                       shortcut='Ctrl+Q',
                       signal='exit'
                       )
                ]

    def config_pages(self):
        from cbpos.mod.base.views import MenuConfigPage, AppConfigPage, LocaleConfigPage
        return [AppConfigPage, MenuConfigPage, LocaleConfigPage]
