################
# Dependencies #
################
import sys
import pathlib
from flask import render_template
from .helpers import delete_chars


################
# Aurora Class #
################
##
# @desc Aurora View to render the specified app view 
##
class View():
    
    ##
    # @desc Constructor method
    ##
    def __init__(self):
        pass


    ##
    # @desc render the view template
    # 
    # @param view: str -- The view template (ex. 'index')
    # @param app: str -- The app name
    # @param code: int -- The http status code (ex. 302)
    # 
    # @var caller: str -- The caller file path
    # @var app: str -- The caller app name
    # @var view_path: str -- The view template path
    # 
    # @return text/html: str -- The rendered template
    ##
    def render(self, view:str, app:str=None, code:int=302, *class_args, **class_kwargs):
        # Remove .html
        view = delete_chars(view, '.html')

        # Check the view
        # User inserted an absolute view template
        if '/' in view:
            view_path = f'{view}.html'

        # User inserted a relative view template
        else:
            # Check app name
            if not app:
                # Inspect the app name from caller file
                caller = sys._getframe().f_back.f_code.co_filename
                app = pathlib.PurePath(caller).parent.name

            view_path = f'{app}/{view}.html'

        # Render the view template      
        return render_template(view_path, *class_args, **class_kwargs), int(code)

