import cbpos
from cbpos.modules import BaseModuleMetadata

class ModuleMetadata(BaseModuleMetadata):
    base_name = 'base'
    version = '0.1.0'
    display_name = 'Base Module'
    dependencies = tuple()
    config_defaults = (
        ('menu', {
                  'show_tab_bar': False,
                  'toolbar_style': 0
                  }
         ),
        ('printing', {
                      'force_preview': False
                      }
         ),
    )
