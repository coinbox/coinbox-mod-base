from PySide import QtGui, QtCore

import cbpos
logger = cbpos.get_logger(__name__)

class AppConfigPage(QtGui.QWidget):
    label = 'Application'
    
    def __init__(self):
        super(AppConfigPage, self).__init__()
        
        self.fullscreen = QtGui.QCheckBox('Fullscreen')
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        form.addRow('Open in fullscreen', self.fullscreen)
        
        self.setLayout(form)

    def populate(self):
        fullscreen = cbpos.config['app', 'fullscreen']
        self.fullscreen.setChecked(fullscreen)
    
    def update(self):
        checked = self.fullscreen.isChecked()
        cbpos.config['app', 'fullscreen'] = checked

class MenuConfigPage(QtGui.QWidget):
    label = 'Menu'
    
    def __init__(self):
        super(MenuConfigPage, self).__init__()
        
        self.show_disabled = QtGui.QCheckBox('Show')
        self.show_empty_root = QtGui.QCheckBox('Show')
        self.show_tab_bar = QtGui.QCheckBox('Show')
        
        self.toolbar_style = QtGui.QComboBox()
        self.toolbar_style.setEditable(False)
        
        # The index in this list is the same as that in the main window
        self.available_styles = (
                  (QtCore.Qt.ToolButtonFollowStyle, "Follow Style"),
                  (QtCore.Qt.ToolButtonIconOnly, "Icon Only"),
                  (QtCore.Qt.ToolButtonTextOnly, "Text Only"),
                  (QtCore.Qt.ToolButtonTextBesideIcon, "Text Beside Icon"),
                  (QtCore.Qt.ToolButtonTextUnderIcon, "Text Under Icon")
                  )
        [self.toolbar_style.addItem(label, i) for i, (style, label) in enumerate(self.available_styles)]
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        form.addRow('Show Disabled Items', self.show_disabled)
        form.addRow('Show Empty Root Items', self.show_empty_root)
        form.addRow('Show Tab Bar', self.show_tab_bar)
        form.addRow('Toolbar Style', self.toolbar_style)
        
        self.setLayout(form)

    def populate(self):
        show_empty_root_items = bool(cbpos.config['menu', 'show_empty_root_items'])
        self.show_empty_root.setChecked(show_empty_root_items)
        
        show_disabled_items = bool(cbpos.config['menu', 'show_disabled_items'])
        self.show_disabled.setChecked(show_disabled_items)
        
        show_tab_bar = bool(cbpos.config['menu', 'show_tab_bar'])
        self.show_tab_bar.setChecked(show_tab_bar)
        
        toolbar_style = cbpos.config['menu', 'toolbar_style']
        try:
            toolbar_style = int(toolbar_style)
        except (ValueError, TypeError):
            style_index = -1
        else:
            style_index = self.toolbar_style.findData(toolbar_style)
        
        if style_index < 0:
            style_index = 0
        self.toolbar_style.setCurrentIndex(style_index)
    
    def update(self):
        cbpos.config['menu', 'show_empty_root_items'] = self.show_empty_root.isChecked()
        
        cbpos.config['menu', 'show_disabled_items'] = self.show_disabled.isChecked()
        
        cbpos.config['menu', 'show_tab_bar'] = self.show_tab_bar.isChecked()
        
        style_index = self.toolbar_style.currentIndex()
        toolbar_style = self.toolbar_style.itemData(style_index)
        cbpos.config['menu', 'toolbar_style'] = unicode(toolbar_style)

class LocaleConfigPage(QtGui.QWidget):
    label = 'Locale'
    
    def __init__(self):
        super(LocaleConfigPage, self).__init__()
        
        self.localedir = QtGui.QLineEdit()
        
        self.languages = QtGui.QLineEdit()
        
        self.fallback = QtGui.QCheckBox('Fallback')
        
        self.codeset = QtGui.QLineEdit()
        
        form = QtGui.QFormLayout()
        form.setSpacing(10)
        
        form.addRow('Locale Directory', self.localedir)
        form.addRow('Languages by order of preference(e.g. en-US,en-UK)', self.languages)
        form.addRow('Fallback to default language?', self.fallback)
        form.addRow('Codeset encoding', self.codeset)
        
        self.setLayout(form)

    def populate(self):
        localedir = cbpos.config['locale', 'localedir']
        languages = cbpos.config['locale', 'languages']
        fallback = bool(cbpos.config['locale', 'fallback'])
        codeset = cbpos.config['locale', 'codeset']
        
        self.localedir.setText(localedir)
        self.languages.setText(','.join(languages))
        self.fallback.setChecked(fallback)
        self.codeset.setText(codeset)
    
    def update(self):
        cbpos.config['locale', 'localedir'] = self.localedir.text()
        cbpos.config['locale', 'languages'] = self.languages.text().split(',')
        cbpos.config['locale', 'fallback'] = self.fallback.isChecked()
        cbpos.config['locale', 'codeset'] = self.codeset.text()
