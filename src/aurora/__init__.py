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


# Descriptions
__version__ = '0.8.17'
__author__ = '<https://github.com/heminsatya>'
