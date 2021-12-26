################
# Dependencies #
################
import sys
import pathlib
from flask import render_template


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
    # @param view: str -- The view template (ex. 'index.html')
    # 
    # @var caller: str -- The caller file path
    # @var app: str -- The caller app name
    # @var view_path: str -- The view template path
    # 
    # @return text/html: str -- The rendered template
    ##
    def render(self, view:str, *class_args, **class_kwargs):
        # Check the view
        # User inserted an absolute view template
        if '/' in view:
            view_path = view

        # User inserted a relative view template
        else:
            # Inspect the app name from caller file
            caller = sys._getframe().f_back.f_code.co_filename
            app = pathlib.PurePath(caller).parent.name
            view_path = f'{app}/{view}'

        # Render the view template      
        return render_template(view_path, *class_args, **class_kwargs)


    ##
    # @desc render the error view template
    # 
    # @param code: int -- The error http code (ex. 400)
    # @param view: str -- The view template (ex. 'index.html')
    # 
    # @var caller: str -- The caller file path
    # @var app: str -- The caller app name
    # @var view_path: str -- The view template path
    # 
    # @return tuple[str, int] -- str: The rendered template -- int: HTTP error code
    ##
    def render_error(self, code:int, view:str, *class_args, **class_kwargs):
        # Check the view
        # User inserted an absolute view template
        if '/' in view:
            view_path = view

        # User inserted a relative view template
        else:
            # Inspect the app name from caller file
            caller = sys._getframe().f_back.f_code.co_filename
            app = pathlib.PurePath(caller).parent.name
            view_path = f'{app}/{view}'

        # Render the view template      
        return render_template(view_path, *class_args, **class_kwargs), int(code)

