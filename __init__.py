import cbpos
from cbpos.modules import BaseModuleLoader

class ModuleLoader(BaseModuleLoader):
    name = 'Base Module'

    def ui_handler(self):
        from .ui import QtUIHandler
        return QtUIHandler()

    def menu(self):
        return [[{'label': 'Main', 'rel': 0, 'priority':5, 'image': self.res('images/menu-main.png')},
                 {'label': 'System', 'rel': -1, 'priority':4, 'image': self.res('images/menu-system.png')},
                 {'label': 'Administration', 'rel': -1, 'priority': 5, 'image': self.res('images/menu-administration.png')}],
                []]

    def config_pages(self):
        from cbpos.mod.base.pages import MenuConfigPage, AppConfigPage, LocaleConfigPage
        return [AppConfigPage, MenuConfigPage, LocaleConfigPage]