# Dependencies
from .Aurora import Aurora
from .Controller import Controller
from .View import View as Template

try:
    from .Forms import Forms
    from .Model import Model
except:
    pass

View = Template().render
Error = Template().render_error


# Descriptions
__version__ = '0.5.4'
__author__ = 'Hemin Satya <https://github.com/heminsatya>'
