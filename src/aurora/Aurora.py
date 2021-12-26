################
# Dependencies #
################
import importlib
from flask import Flask


################
# Aurora Class #
################
##
# @desc Aurora class to serve the root application and it's child apps 
##
class Aurora():

    ##
    # @desc Constructor method
    #
    # @property app: NoneType -- Placeholder for the root app (Flask Instance)
    # @property config: module -- The config module
    # @property debug: bool -- The debug mode
    # @property apps: module -- The _apps module
    ##
    def __init__(self):
        # The root app
        self.app = None
        
        # Import the config module
        self.config = importlib.import_module("config")

        # Debug mode
        self.debug = getattr(self.config, "DEBUG")
        
        # Import the _apps module
        self.apps = importlib.import_module("_apps")

        # Try to serve the root app
        try:
            self.serve()
        
        # Except errors
        except NameError as err:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(err)


    ##
    # @desc The serve method -- Serves the root application and its child apps
    #
    # @var apps: dict -- The APPS attribute of the _apps module
    # @var root_path: str -- The root app path
    # @var default_app: str -- The DEFAULT_APP attribute of the config module
    # @var statics: str -- The STATICS attribute of the config module
    # @var secret_key: str -- The SECRET_KEY attribute of the config module
    # @var globals: dict -- The GLOBALS attribute of the config module
    # @var supported_apis: list -- The supported database APIs for the selected database engine
    # @var error: str -- The error message on error
    # @var app: object -- The root application
    #
    # @decorator context_processor: function -- For decorating global_variables local method
    # @method global_variables: function -- A local method for setting global variables
    #
    # @return object -- The root app
    ##
    def serve(self):
        # Fetch the required attributes
        apps = getattr(self.apps, "apps")
        root_path = getattr(self.config, "ROOT_PATH")
        statics = getattr(self.config, 'STATICS')
        secret_key = getattr(self.config, "SECRET_KEY")

        # Initialize the root app (Flask instance)
        self.app = Flask(__name__, template_folder=f'{root_path}/views', static_folder=f'{root_path}/{statics}')
        
        # Set the app secret key
        self.app.config['SECRET_KEY'] = secret_key


        ##
        # @desc The local global_variables method -- Sets the global variables usable in views
        #
        # @var global_dict: dict -- A dictionary for all global variables (GLOBALS + Auto Globals)
        # @var translate dict -- Uppercase key version of global_dict
        #
        # @return dict -- Global variables dictionary
        ##
        app = self.app
        @app.context_processor
        def global_variables():
            translate = {}
            auto_globals = {}

            # Global attibutes
            error_app = getattr(self.config, 'ERROR_APP')
            default_app = getattr(self.config, 'DEFAULT_APP')
            globals = getattr(self.config, 'GLOBALS')
            
            # Auto globals
            auto_globals = {
                'error_app': apps[error_app],
                'default_app': apps[default_app],
                'statics': statics,
            }

            # Add apps
            auto_globals.update(apps)

            # Add global variables
            auto_globals.update(globals)

            # Translate auto_globals to uppercase
            for k, v in auto_globals.items():
                translate[k.upper()] = v
            
            # Return the translated dictionary
            return translate

        # Try to bootstrap the apps
        try:
            # Bootstrap installed apps (child apps)
            self.bootstrap(apps)

            # Return the root app
            return self.app
        
        # Handle errors
        except NameError as err:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Return the result
            else:
                return False


    ##
    # @desc The bootstrap method -- Bootsraps the child apps modules and packages
    #
    # @param apps: dict -- The child apps to serve
    # @param default_app: string -- The default app to serve the '/' url
    #
    # @var module: module -- The _controllers module
    # @var controllers: list -- The controllers attribute of the _controllers module
    #
    # @return bool
    ##
    def bootstrap(self, apps:dict):
        # Check the child apps
        if apps:
            # Import app modules and packages
            for app in apps:
                # Import the _controllers module
                module = importlib.import_module(f"controllers.{app}._controllers")

                # Fetch the controllers attribute
                controllers = getattr(module, "controllers")
                
                # Try to call the router method
                try:
                    self.router(app, controllers, apps)

                # Something went wrong
                except NameError as err:
                    # Check debug mode
                    if self.debug:
                        # Raise error
                        raise Exception(err)

                    # Return the result
                    else:
                        return False
            
            # Everything is OK
            return True


    ##
    # @desc The app router method -- Routes a controller for each route(url)
    #
    # @param app: str -- The child app to route
    # @param controllers: list -- The child app controllers
    # @param apps: dict -- The child apps to route
    # @param default_app: string -- The default app to route
    #
    # @var error_app: str -- The ERROR_APP attribute of the config module
    # @var default_app: str -- The DEFAULT_APP attribute of the config module
    # @var Module: module -- The controller module
    # @var Controller: class -- The controller class
    # @var methods: list -- ['GET'], ['POST'], ['GET', 'POST'] -- default: ['GET']
    # @var rule: str -- URL rule for a route
    # @var endpoint: str -- Endpoint for a route
    # 
    # @return None
    ##
    def router(self, app:str, controllers:list, apps:dict) -> None:
        error_app = getattr(self.config, 'ERROR_APP')
        default_app = getattr(self.config, 'DEFAULT_APP')

        for controller in controllers:

            # Recognize the controller
            Module = importlib.import_module(f"controllers.{app}.{controller[0]}")
            Controller = getattr(Module, controller[0])

            # Check for the mothods
            if len(controller) == 3:
                methods=controller[2]
            else:
                methods=['GET']

            # Check the URL rule
            if controller[1] == '':
                rule = f'/{apps[app]}/'
                endpoint = app
            else:
                rule = f'/{apps[app]}/{controller[1]}/'
                endpoint = f'{app}-{controller[1]}'

            # Generate the view function
            view_func = Controller.as_view(endpoint)

            # Check the apps
            # Error pages app
            if app == error_app:
                # Errors on abort
                self.app.register_error_handler(int(controller[1]), Controller.err)

                # Errors on GET method for developer
                if self.debug:
                    self.app.add_url_rule(rule=rule, endpoint=endpoint, view_func=view_func, methods=methods)

            # Other apps
            else:

                # Root app index controller
                if app == default_app and controller[1] == '':
                    self.app.add_url_rule(rule='/', endpoint='default-app', view_func=view_func, methods=methods)

                # All apps controllers
                self.app.add_url_rule(rule=rule, endpoint=endpoint, view_func=view_func, methods=methods)


    ##
    # @desc The run method -- Runs the root app
    # 
    # @var host: str -- The HOST attribute of the config module
    # @var port: str -- The PORT attribute of the config module
    # 
    # @return object: NoneType -- The root app
    ##
    def run(self):    
        # Fetch the required attributes
        host = getattr(self.config, "HOST")
        port = getattr(self.config, "PORT")

        # Try to run the app
        try:
            return self.app.run(host=host, port=port, debug=self.debug)

        except NameError as err:
            # Check debug mode
            if self.debug:
                # Raise error
                raise Exception(err)

            # Return the result
            else:
                return False

