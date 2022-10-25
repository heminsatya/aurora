# Dependencies
from .Aurora import Aurora

# For the sake of init_app
try:
    from .Controller import Controller
    from .Template import Template
    from .Forms import Forms
    from .Model import Model

    View = Template().render

# Pass on error
except:
    pass

# Descriptions
__version__ = '0.8.20'
__author__ = '<https://github.com/heminsatya>'
