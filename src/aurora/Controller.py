################
# Dependencies #
################
import sys
import pathlib
import importlib
from aurora.security import request, redirect, check_cookie, get_cookie, check_session, get_session, set_session
from aurora.helpers import app_exists
from flask.views import View


####################
# Controller Class #
####################
##
# @desc Controller class to control views based on the requested method 
##
class Controller(View):

    ##
    # @desc Constructor method -- Generates Pluggable Views
    ##
    def __init__(self) -> None:
        # Required modules
        config = importlib.import_module('config')

        # Required attributes
        self.default_lang = getattr(config, 'DEFAULT_LANG') 
        self.multi_lang = getattr(config, "MULTI_LANG")
        self.languages = getattr(config, 'LANGUAGES') 

        # Public properties
        self.active_lang = self.default_lang
        self.LANGUAGE = ''

        # Inspect the app name from caller file
        caller = sys._getframe().f_back.f_code.co_filename
        self.app_name = pathlib.PurePath(caller).parent.name
        self.app_url = app_exists(self.app_name)['url'] if app_exists(self.app_name)['result'] else False

        # Check the language
        if self.multi_lang:
            # Fetch the lang
            path = request.path
            lang = path.split('/')[1]

            # The root path and apps path
            if path == '/' or lang == self.app_url or app_exists(lang)['result']:
                # active_lang cookie exists
                if check_cookie('active_lang'):
                    self.active_lang = get_cookie('active_lang')
                    set_session('active_lang', get_cookie('active_lang'))

                # active_lang session exists
                elif check_session('active_lang'):
                    self.active_lang = get_session('active_lang')

                # Neighter active_lang cookie nor active_lang session exists
                else:
                    self.active_lang = self.default_lang
                    set_session('active_lang', self.default_lang)

            # Languages path
            elif lang in self.languages:
                self.active_lang = lang
                set_session('active_lang', lang)

            # Other paths
            else:
                self.active_lang = self.default_lang
                set_session('active_lang', self.default_lang)

            # Set active language URL
            self.LANGUAGE = '/' + self.active_lang


    ##
    # @desc Flask dispatch_request method -- Generates Pluggable Views
    ##
    def dispatch_request(self, *class_args, **class_kwargs):
        # Check the requested methods then return the related view function
        # The 'POST' request
        if request.method == 'POST':
            return self.post(*class_args, **class_kwargs)

        # The 'GET' request
        elif request.method == 'GET':
            # Check the language
            if self.multi_lang:
                # Fetch the path
                path = request.path

                # The root path
                # if path == '/' or app_exists(path.split('/')[1])['result']:
                if path == '/' or path.split('/')[1] == self.app_url or app_exists(path.split('/')[1])['result']:
                    if check_cookie('active_lang'):
                        return redirect('/' + get_cookie('active_lang') + path)

                    elif check_session('active_lang'):
                        return redirect('/' + get_session('active_lang') + path)

                    else:
                        return redirect('/' + self.default_lang + path)

            return self.get(*class_args, **class_kwargs)

        # The 'PUT' request
        elif request.method == 'PUT':
            return self.put(*class_args, **class_kwargs)

        # The 'DELETE' request
        elif request.method == 'DELETE':
            return self.delete(*class_args, **class_kwargs)


    ##
    # @desc get method placeholder -- To handle the 'GET' requests
    # 
    # @return any
    ##
    def post(self):
        return 'POST Method'


    ##
    # @desc get method placeholder -- To handle the 'GET' requests
    # 
    # @return any
    ##
    def get(self):
        return 'GET Method'
     

    ##
    # @desc get method placeholder -- To handle the 'GET' requests
    # 
    # @return any
    ##
    def put(self):
        return 'PUT Method'
     

    ##
    # @desc get method placeholder -- To handle the 'DELETE' requests
    # 
    # @return any
    ##
    def delete(self):
        return 'DELETE Method'

