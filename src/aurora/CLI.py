################
# Dependencies #
################
import os
import platform
import importlib
import click
from datetime import datetime
from .helpers import *
from .SQL import Database

# Instantiate the Database class
db = Database()

# Aurora path
aurora_path = os.path.dirname(__file__)

# App path (the caller)
app_path = os.getcwd()

# Check platform system
# Windows
if platform.system() == 'Windows':
    url_div = '\\'

# Linux, Mac
else:
    url_div = '/'

# Fetch statics
config = importlib.import_module('config')
statics = getattr(config, "STATICS")

# Fetch registered apps
apps_module = importlib.import_module('_apps')
apps = getattr(apps_module, "apps")

# Fetch registered models
models_module = importlib.import_module('models._models')
models = getattr(models_module, "models")

# The database (file)
database = getattr(config, "DB_CONFIG")['database']


#############
# CLI Class #
#############
##
# @desc CLI class for manage the root app and its child apps
##
class CLI:
    ##
    # @desc Constructor method
    ##
    def __init__(self):

        # Try to run the CLI application
        try:
            # Call the group method
            self.group()

            # Call the cli method
            self.cli()

        # Handle errorr
        except NameError as err:
            raise Exception(err)


    ##
    # @desc group method for grouping commands together
    ##
    def group(self):
        self.cli.add_command(self.create_app)
        self.cli.add_command(self.delete_app)
        self.cli.add_command(self.create_controller)
        self.cli.add_command(self.delete_controller)
        self.cli.add_command(self.create_view)
        self.cli.add_command(self.delete_view)
        self.cli.add_command(self.create_model)
        self.cli.add_command(self.delete_model)
        self.cli.add_command(self.create_form)
        self.cli.add_command(self.delete_form)
        self.cli.add_command(self.check_db)
        self.cli.add_command(self.init_db)
        self.cli.add_command(self.migrate_db)


    ##
    # @desc cli method for grouping other methods
    ##
    @click.group()
    def cli():
        pass


    ##
    # @desc create_app method for creating new child apps
    # 
    # @var name: str -- The app name
    # @var url: str -- The app base URL
    ##
    @click.command()
    def create_app():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App name is taken
                if name in apps:
                    print(f'The "{name}" is already registered. Try another name.')

                # App name is OK
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Prompt for base URL
        while True:
            url = input("Base URL: ")

            # Check base URL
            if base_url(url)['result']:
                # Base URL is taken
                if url in apps.values():
                    print(f'The "{url}" is already registered. Try another URL.')

                # Base URL is OK
                else:
                    break

            # Print the error
            else:
                print(base_url(url)['message'])
        
        # Begin the process
        try:
            print('Creating the new app...')

            # Create folders: (controllers, forms, statics, views)
            make_dir(f'{app_path + url_div}controllers{url_div + name}')
            make_dir(f'{app_path + url_div}forms{url_div + name}')
            make_dir(f'{app_path + url_div + statics + url_div + name}')
            make_dir(f'{app_path + url_div}views{url_div + name}')

            # Handle controllers blueprint (copy, unzip, delete)
            controllers_blueprint= f'{aurora_path + url_div}blueprints{url_div}controllers.zip'
            controllers_file = f'{app_path + url_div}controllers{url_div + name + url_div}controllers.zip'
            controllers_dir = f'{app_path + url_div}controllers{url_div + name + url_div}'
            copy_file(controllers_blueprint, controllers_file)
            unzip_file(controllers_file, controllers_dir)
            delete_file(controllers_file)

            # Handle forms blueprint (copy, unzip, delete)
            forms_blueprint= f'{aurora_path + url_div}blueprints{url_div}forms.zip'
            forms_file = f'{app_path + url_div}forms{url_div + name + url_div}forms.zip'
            forms_dir = f'{app_path + url_div}forms{url_div + name + url_div}'
            copy_file(forms_blueprint, forms_file)
            unzip_file(forms_file, forms_dir)
            delete_file(forms_file)

            # Handle statics blueprint (copy, unzip, delete)
            statics_blueprint= f'{aurora_path + url_div}blueprints{url_div}statics.zip'
            statics_file = f'{app_path + url_div + statics + url_div + name + url_div}statics.zip'
            statics_dir = f'{app_path + url_div + statics + url_div + name + url_div}'
            copy_file(statics_blueprint, statics_file)
            unzip_file(statics_file, statics_dir)
            delete_file(statics_file)

            # Handle views blueprint (copy, unzip, delete)
            views_blueprint= f'{aurora_path + url_div}blueprints{url_div}views.zip'
            views_file = f'{app_path + url_div}views{url_div + name + url_div}views.zip'
            views_dir = f'{app_path + url_div}views{url_div + name + url_div}'
            copy_file(views_blueprint, views_file)
            unzip_file(views_file, views_dir)
            delete_file(views_file)

            # Update layout.html
            replace_file_string(f'{app_path + url_div}views{url_div + name + url_div}layout.html', 'app_name', name)

            # Update _apps.py
            new_line = f'''    '{name}': '{url}',\n'''
            new_line += '''}#do-not-change-me'''
            replace_file_line(file_path=f'{app_path + url_div}_apps.py', old_line='}#do-not-change-me', new_line=new_line)

            # print the message
            print('The new app created successfully!')

        # Handle errors
        except NameError as err:
            print(err)


    ##
    # @desc delete_app method for removing child apps
    ##
    @click.command()
    def delete_app():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])
        
        # Alert the user for data loss
        alert = '''You will loose the following data perminantly:\n'''
        alert += f'''  {app_path + url_div}controllers{url_div + name + url_div}*\n'''
        alert += f'''  {app_path + url_div}forms{url_div + name + url_div}*\n'''
        alert += f'''  {app_path + url_div + statics + url_div + name + url_div}*\n'''
        alert += f'''  {app_path + url_div}views{url_div + name + url_div}*\n'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            print('Removing the app...')

            # Begin the process
            try:
                # Delete the app folders
                delete_dir(f'{app_path + url_div}controllers{url_div + name + url_div}')
                delete_dir(f'{app_path + url_div}forms{url_div + name + url_div}')
                delete_dir(f'{app_path + url_div + statics + url_div + name + url_div}')
                delete_dir(f'{app_path + url_div}views{url_div + name + url_div}')

                # Update the _apps.py
                url = apps[name]
                old_line = f"""'{name}': '{url}',"""
                replace_file_line(file_path=f'{app_path + url_div}_apps.py', old_line=old_line, new_line='')
                
                print('App deleted successfully')

            # Handle errors
            except NameError as err:
                print(err)

        # Rejected
        else:
            print('The operation canceled!')
            exit()


    ##
    # @desc create_controller method for creating new controller
    ##
    @click.command()
    def create_controller():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Controllers info
        module = importlib.import_module(f'controllers.{name}._controllers')
        controllers = getattr(module, 'controllers')

        # Controller name
        break_loop = False
        while True:
            # Check break loop from for loop
            if break_loop:
                break
            
            # Prompt for controller name
            ctrl = input("Controller Name: ")

            # Check controller name
            if controller_name(ctrl)['result']:
                if len(controllers) == 0:
                    break

                # Controller already exists
                for controller in controllers:
                    if ctrl in controller:
                        print(f'The "{ctrl}" already exists!')
                        break

                    # Controller not exists
                    else:
                        break_loop = True
                        break

            # Print the error
            else:
                print(controller_name(ctrl)['message'])

        # Prompt for controller url
        break_loop = False
        while True:
            # Check break loop from for loop
            if break_loop:
                break
            
            # Prompt for controller url
            if len(controllers) == 0:
                url = input("Controller URL (optional): ")
            else:
                url = input("Controller URL: ")

            # Check controller url
            if controller_url(url)['result']:
                if len(controllers) == 0:
                    break

                # Controller url already exists
                for controller in controllers:
                    if url in controller:
                        print(f'The "{url}" already exists!')
                        break

                    # Controller url not exists
                    else:
                        break_loop = True
                        break

            # Print the error
            else:
                print(controller_url(url)['message'])

        # Prompt for optional methods
        while True:
            methods = input("Methods (optional): ").upper()

            # Remove spaces from methods
            methods = delete_chars(methods, ' ')
            
            # Convert methods to list 
            if methods:
                methods = methods.split(',')

            # Sort methods
            methods = sorted(methods)

            # Check methods
            if not controller_methods(methods)['result']:
                print(controller_methods(methods)['message'])

            # Break the loop
            else:
                break
        
        # Controller methods
        ctrl_methods = ''

        # POST method
        if 'POST' in methods:
            ctrl_methods += """    # POST Method\n"""
            ctrl_methods += """    def post(self):\n"""
            ctrl_methods += """        pass\n\n"""

        # GET method
        if 'GET' in methods:
            ctrl_methods += """    # GET Method\n"""
            ctrl_methods += """    def get(self):\n"""
            ctrl_methods += """        return 'Page content...'\n\n"""

        # PUT method
        if 'PUT' in methods:
            ctrl_methods += """    # PUT Method\n"""
            ctrl_methods += """    def put(self):\n"""
            ctrl_methods += """        pass\n\n"""

        # DELETE method
        if 'DELETE' in methods:
            ctrl_methods += """    # DELETE Method\n"""
            ctrl_methods += """    def delete(self):\n"""
            ctrl_methods += """        pass\n\n"""

        # Default method (GET)
        if not methods:
            ctrl_methods += """    # GET Method\n"""
            ctrl_methods += """    def get(self):\n"""
            ctrl_methods += """        return 'Page content...'\n\n"""
        
        # try the process
        try:
            # Create controller
            print('Creating the controller...')
            
            # Controller blueprint
            controller_blueprint = f'{aurora_path + url_div}blueprints{url_div}controller.zip'
            controller_file = f'{app_path + url_div}controllers{url_div + name + url_div}controller.zip'
            controller_dir = f'{app_path + url_div}controllers{url_div + name + url_div}'

            # Copy, unzip, delete blueprint
            copy_file(controller_blueprint, controller_file)
            unzip_file(controller_file, controller_dir)
            delete_file(controller_file)

            # Rename _controller.py
            controller_old = f'{app_path + url_div}controllers{url_div + name + url_div}_controller.py'
            controller_new = f'{app_path + url_div}controllers{url_div + name + url_div + ctrl}.py'
            rename_file(controller_old, controller_new)

            # Update new controller
            replace_file_string(controller_new, 'ControllerName', ctrl)
            replace_file_line(controller_new, '...', ctrl_methods)

            # Update _controllers.py
            controllers_file = f'{app_path + url_div}controllers{url_div + name + url_div}_controllers.py'

            if methods:
                controller_data = f"""   ('{ctrl}', '{url}', {methods}),\n"""
            else:
                controller_data = f"""   ('{ctrl}', '{url}'),\n"""

            controller_data += """]#do-not-change-me"""

            replace_file_line(controllers_file, ']#do-not-change-me', controller_data)

            # Print result
            print('The new controller created successfuly!')

        # Handle errors
        except NameError as err:
            print(err)


    ##
    # @desc delete_controller method for removing an existing controller
    ##
    @click.command()
    def delete_controller():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Controllers info
        module = importlib.import_module(f'controllers.{name}._controllers')
        controllers = getattr(module, 'controllers')

        # App controllers
        if len(controllers) == 0:
            print(f'No controllers found for the {name}!')
            exit()

        # Controller name
        break_loop = False
        while True:
            # Check break loop from for loop
            if break_loop:
                break
            
            # Prompt for controller name
            ctrl = input("Controller Name: ")

            # Check controller name
            if controller_name(ctrl)['result']:
                i = 1
                for controller in controllers:
                    # Controller exists
                    if ctrl in controller:
                        break_loop = True
                        break

                    # Controller not exists
                    else:
                        if len(controllers) == i:
                            print(f'The "{ctrl}" does\'nt exist!')

                    i += 1

            # Print the error
            else:
                print(controller_name(ctrl)['message'])
        
        # Alert the user for data loss
        alert = '''You will loose the following data perminantly:\n'''
        alert += f'''  {app_path + url_div}controllers{url_div + name + url_div + ctrl}.py\n'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            print('Removing the controller...')

            # Begin the process
            try:
                # Delete the controller module
                delete_file(f'{app_path + url_div}controllers{url_div + name + url_div + ctrl}.py')

                # Update _controllers.py
                controllers_file = f'{app_path + url_div}controllers{url_div + name + url_div}_controllers.py'
                replace_file_line(controllers_file, f"('{ctrl}',", '')
                
                print('Controller deleted successfully')

            # Handle errors
            except NameError as err:
                print(err)

        # Rejected
        else:
            print('The operation canceled!')
            exit()


    ##
    # @desc create_view method for creating new view
    ##
    @click.command()
    def create_view():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Prompt for view name
        while True:
            view = input("View Name: ")

            # Check the view name
            if view_name(view)['result']:
                view_file = f'{app_path + url_div}views{url_div + name + url_div + view}.html'

                # View exists
                if os.path.exists(view_file):
                    print(f'The "{view}" is already exists!')

                # View not exists
                else:
                    break

            # Print the error
            else:
                print(view_name(view)['message'])

        # Begin the process
        try:
            print('Creating the new view...')
            
            # View blueprint
            view_blueprint = f'{aurora_path + url_div}blueprints{url_div}view.zip'
            view_file = f'{app_path + url_div}views{url_div + name + url_div}view.zip'
            view_dir = f'{app_path + url_div}views{url_div + name + url_div}'
            
            # Copy the view blueprint
            copy_file(view_blueprint, view_file)

            # Unzip the view blueprint
            unzip_file(view_file, view_dir)

            # Delete the view zip file
            delete_file(view_file)

            # Rename the view blueprint
            old_view = f'{app_path + url_div}views{url_div + name + url_div}_view.html'
            new_view = f'{app_path + url_div}views{url_div + name + url_div + view}.html'
            rename_file(old_view, new_view)

            # update the view blue print
            replace_file_string(new_view, 'app_name', name)

            # Print the result
            print('The new view created successfully!')
        
        # Handle errors
        except NameError as err:
            print(err)


    ##
    # @desc delete_view method for removing an existing view
    ##
    @click.command()
    def delete_view():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Prompt for view name
        while True:
            view = input("View Name: ")

            # Check the view name
            if view_name(view)['result']:
                view_file = f'{app_path + url_div}views{url_div + name + url_div + view}.html'

                # View not exists
                if not os.path.exists(view_file):
                    print(f'The "{view}" deos\'nt exist!')

                # View exists
                else:
                    break

            # Print the error
            else:
                print(view_name(view)['message'])
        
        # Alert the user for data loss
        alert = '''You will loose the following data perminantly:\n'''
        alert += f'''  {app_path + url_div}views{url_div + name + url_div + view}.html\n'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Removing the view...')

                # Delete the view file
                view_file = f'{app_path + url_div}views{url_div + name + url_div + view}.html'
                delete_file(view_file)

                # Print the result
                print('The view deleted successfully!')

            # Handle errors
            except NameError as err:
                print(err)

        # Rejected
        else:
            print('The operation canceled!')
            exit()


    ##
    # @desc create_model method for creating new model
    ##
    @click.command()
    def create_model():
        # Prompt for model name
        while True:
            model = input("Model Name: ")

            # Check model name
            if model_name(model)['result']:
                # Model exists
                if model in models:
                    print(f'The "{model}" already exist!')

                # Model not exists
                else:
                    break

            # Print the error
            else:
                print(model_name(model)['message'])

        # Begin the process
        try:
            print('Creating the new model...')

            # Model blueprint
            model_blueprint = f'{aurora_path + url_div}blueprints{url_div}model.zip'
            model_file = f'{app_path + url_div}models{url_div}model.zip'
            model_dir = f'{app_path + url_div}models{url_div}'
            
            # Copy the model blueprint
            copy_file(model_blueprint, model_file)

            # Unzip the model blueprint
            unzip_file(model_file, model_dir)

            # Delete the model zip file
            delete_file(model_file)

            # Rename the _model.py
            old_model = f'{app_path + url_div}models{url_div}_model.py'
            new_model = f'{app_path + url_div}models{url_div + model}.py'
            rename_file(old_model, new_model)

            # Update the model blue print
            replace_file_string(new_model, 'ModelName', model)
            replace_file_string(new_model, '_table_name', snake_case(model))

            # Update the _models.py
            models_file = f'{app_path + url_div}models{url_div}_models.py'

            models_data = f"""    '{model}',\n"""
            models_data += """)#do-not-change-me"""

            replace_file_line(models_file, ')#do-not-change-me', models_data)

            # Update the __init__.py
            init_file = f'{app_path + url_div}models{url_div}__init__.py'

            if len(models) == 0:
                replace_file_line(init_file, '...', '')

            init_data = f"""    from .{model} import {model}\n"""
            init_data += """    #do-not-change-me\n"""

            replace_file_line(init_file, '#do-not-change-me', init_data)

            # Print the result
            print('The new model created successfully!')
        
        # Handle errors
        except NameError as err:
            print(err)


    ##
    # @desc delete_model method for removing an existing model
    ##
    @click.command()
    def delete_model():
        # Prompt for model name
        while True:
            model = input("Model Name: ")

            # Check model name
            if model_name(model)['result']:
                # Model not exists
                if not model in models:
                    print(f'The "{model}" doesn\'t exist!')

                # Model exists
                else:
                    break

            # Print the error
            else:
                print(model_name(model)['message'])
        
        # Alert the user for data loss
        alert = '''You will loose the following data perminantly:\n'''
        alert += f'''  {app_path + url_div}models{url_div + model}.py\n'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Removing the model...')

                # Delete the model module
                model_file = f'{app_path + url_div}models{url_div + model}.py'
                delete_file(model_file)

                # Update the _models.py
                models_file = f'{app_path + url_div}models{url_div}_models.py'
                replace_file_line(models_file, f"'{model}',", '')

                # Update the __init__.py
                init_file = f'{app_path + url_div}models{url_div}__init__.py'

                if len(models) == 1:
                    replace_file_line(init_file, f'from .{model} import {model}', '    ...\n')
                else:
                    replace_file_line(init_file, f'from .{model} import {model}', '')

                # Print the result
                print('The model deleted successfully!')

            # Handle errors
            except NameError as err:
                print(err)

        # Rejected
        else:
            print('The operation canceled!')
            exit()


    ##
    # @desc create_form method for creating new form
    ##
    @click.command()
    def create_form():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Fetch registered forms for the app
        forms_module = importlib.import_module(f'forms.{name}._forms')
        forms = getattr(forms_module, "forms")
        
        # Prompt for form name
        while True:
            form = input("Form Name: ")

            # Check form name
            if form_name(form)['result']:
                # Form exists
                if form in forms:
                    print(f'The "{form}" already exist!')

                # Form not exists
                else:
                    break

            # Print the error
            else:
                print(form_name(form)['message'])

        # Begin the process
        try:
            print('Creating the new form...')

            # Form blueprint
            form_blueprint = f'{aurora_path + url_div}blueprints{url_div}form.zip'
            form_file = f'{app_path + url_div}forms{url_div + name + url_div}form.zip'
            form_dir = f'{app_path + url_div}forms{url_div + name + url_div}'
            
            # Copy the form blueprint
            copy_file(form_blueprint, form_file)

            # Unzip the form blueprint
            unzip_file(form_file, form_dir)

            # Delete the forms zip file
            delete_file(form_file)

            # Rename the _form.py
            old_form = f'{app_path + url_div}forms{url_div + name + url_div}_form.py'
            new_form = f'{app_path + url_div}forms{url_div + name + url_div + form}.py'
            rename_file(old_form, new_form)

            # Update the form blue print
            replace_file_string(new_form, 'FormName', form)

            # Update the _forms.py
            forms_file = f'{app_path + url_div}forms{url_div + name + url_div}_forms.py'

            forms_data = f"""    '{form}',\n"""
            forms_data += """)#do-not-change-me"""

            replace_file_line(forms_file, ')#do-not-change-me', forms_data)

            # Update the __init__.py
            init_file = f'{app_path + url_div}forms{url_div + name + url_div}__init__.py'

            if len(forms) == 0:
                replace_file_line(init_file, '...', '')

            init_data = f"""    from .{form} import {form}\n"""
            init_data += """    #do-not-change-me\n"""

            replace_file_line(init_file, '#do-not-change-me', init_data)

            # Print the result
            print('The new form created successfully!')
        
        # Handle errors
        except NameError as err:
            print(err)


    ##
    # @desc delete_form method for removing an existing form
    ##
    @click.command()
    def delete_form():
        # Prompt for app name
        while True:
            name = input("App Name: ")

            # Check app name
            if app_name(name)['result']:
                # App not exists
                if not name.lower() in apps:
                    print(f'The "{name}" doesn\'t exist!')

                # App exists
                else:
                    break

            # Print the error
            else:
                print(app_name(name)['message'])

        # Fetch registered forms for the app
        forms_module = importlib.import_module(f'forms.{name}._forms')
        forms = getattr(forms_module, "forms")
        
        # Prompt for form name
        while True:
            form = input("Form Name: ")

            # Check form name
            if form_name(form)['result']:
                # Form not exists
                if not form in forms:
                    print(f'The "{form}" doesn\'t exist!')

                # Form exists
                else:
                    break

            # Print the error
            else:
                print(form_name(form)['message'])
        
        # Alert the user for data loss
        alert = '''You will loose the following data perminantly:\n'''
        alert += f'''  {app_path + url_div}forms{url_div + name + url_div + form}.py\n'''
        
        # Print the alert
        print(alert)

        # Prompt the user for confirmation
        confirm = input("Do you want to continue? (yes/no) ")
            
        # Confirmed
        if confirm.lower() == 'yes':
            # Begin the process
            try:
                print('Removing the form...')

                # Delete the form module
                form_file = f'{app_path + url_div}forms{url_div + name + url_div + form}.py'
                delete_file(form_file)

                # Update the _forms.py
                forms_file = f'{app_path + url_div}forms{url_div + name + url_div}_forms.py'
                replace_file_line(forms_file, f"'{form}',", '')

                # Update the __init__.py
                init_file = f'{app_path + url_div}forms{url_div + name + url_div}__init__.py'

                if len(forms) == 1:
                    replace_file_line(init_file, f'from .{form} import {form}', '    ...\n')
                else:
                    replace_file_line(init_file, f'from .{form} import {form}', '')

                # Print the result
                print('The form deleted successfully!')

            # Handle errors
            except NameError as err:
                print(err)

        # Rejected
        else:
            print('The operation canceled!')
            exit()


    ##
    # @desc check_db method for checking the database for existence and so on
    ##
    @click.command()
    def check_db():
        # Check database existence
        if not db._exist_database(database):
            # Prepare the alert message
            alert = '''Database connection established successfully!\n'''
            alert += '''Database not initialized!\n'''
            alert += '''To initialize the database run the following command:\n'''
            alert += '''python manage.py init-db'''
            
            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check the database migrations table
        if not db._exist_table('migrations'):
            # Prepare the alert message
            alert = '''Database not supported!\n'''
            alert += '''Make sure you initialized the database correctly, using the following command:\n'''
            alert += '''python manage.py init-db'''
            
            # Alert the user
            print(alert)

            # Exit the program
            exit()

        # Check the models for any errors
        if True:
            ...
            print('Checking models for any errors...')
            print('Work in progress.')

        # Check the available unmigrated changes
        if True:
            ...
            print('Checking models for unapplied changes...')
            print('Work in progress.')

        # Check the available migrations
        if True:
            ...
            print('Checking database for available migrations...')
            print('Work in progress.')

        # Exit the program
        exit()


    ##
    # @desc init_db method for initializing the database for the first time
    ##
    @click.command()
    def init_db():
        # db._delete_database(database=database, confirm=True)

        # Check database existence
        if db._exist_database(database):
            # Prepare the alert message
            alert = '''Database already exists!\n'''
            alert += '''To check the database run the following command:\n'''
            alert += '''python manage.py check-db'''
            
            # Alert the user
            print(alert)

        # Initialize the database
        else:
            print('Initializing the database...')

            # Attempt the process
            try:
                # Create the database
                db._create_database(database=database)

                # Create the migrations table
                new_db = Database()
                col_type = {
                    'id': 'integer',
                    'version': 'varchar(100)',
                    'current': 'boolean',
                    'date': 'date',
                    'comment': 'text',
                }
                primary_key = 'id'
                unique = ['version']
                not_null = ['version', 'current', 'date']
                default = {
                    'current': False,
                }
                new_db._create_table(table='migrations', col_type=col_type, primary_key=primary_key, unique=unique, not_null=not_null, default=default)

                # print()

                # Migration content placeholder
                migration_content = ''

                # Models collection for migrations
                models_coll = f"""_models = {models}\n\n"""

                # Update migrations content
                migration_content += models_coll

                # Create the users' tables (models)
                for model in models:
                    # Find the model and its class
                    Model = importlib.import_module(f'models.{model}')
                    Class = getattr(Model, model)

                    # The table name
                    table = Class().table

                    # Atributes dictionary
                    attrs = {}

                    # Add model columns (class attributes) to attrs
                    attrs.update(dict([(x,y) for x,y in Class.__dict__.items() if not x.startswith('__')]))

                    # Table default parameters
                    col_type = {}
                    primary_key = Class().primary_key
                    unique = []
                    not_null = []
                    default = {}
                    foreign_key = {}

                    # New attrs
                    new_attrs = {}

                    # Final attrs
                    final_attrs = {}

                    # Check primary key
                    if primary_key == None:
                        # Check the id column
                        if 'id' in attrs:
                            # Set primary key
                            primary_key = 'id'

                        else:
                            # Set primary key
                            primary_key = 'id'

                            # Add id to new attrs
                            new_attrs['id'] = {'datatype': 'integer', 'unique': False, 'not_null': True, 'default': None, 'check': None, 'foreign_key': None, 'on_update': None, 'on_delete': None}

                    # Update new attrs
                    new_attrs.update(attrs)

                    # Loop the model attributes
                    for x in new_attrs:

                        # Column + Datatype
                        col_type[x] = new_attrs[x]['datatype']

                        # UNIQUE
                        if new_attrs[x]['unique']:
                            unique.append(x)

                        # NOT NULL
                        if new_attrs[x]['not_null']:
                            not_null.append(x)

                        # DEFAULT
                        if new_attrs[x]['default'] != None:
                            default[x] = new_attrs[x]['default']

                        # Foreign key
                        if new_attrs[x]['related_to']:
                            # Find the reference model and its class
                            r_model = importlib.import_module(f"models.{new_attrs[x]['related_to']}")
                            r_class = getattr(r_model, new_attrs[x]['related_to'])

                            r_table = r_class().table
                            r_column = r_class().primary_key if r_class().primary_key else 'id'

                            foreign_key[x] = {
                                'r_table': r_table,
                                'r_column': r_column,
                                'on_update': new_attrs[x]['on_update'],
                                'on_delete': new_attrs[x]['on_delete'],
                            }

                    # Create the model table
                    new_db._create_table(table=table, col_type=col_type, primary_key=primary_key, unique=unique, not_null=not_null, default=default, foreign_key=foreign_key)

                    # Produce final attrs for migrations
                    final_attrs['table'] = table
                    final_attrs['col_type'] = col_type
                    final_attrs['primary_key'] = primary_key
                    final_attrs['unique'] = unique
                    final_attrs['not_null'] = not_null
                    final_attrs['default'] = default
                    final_attrs['foreign_key'] = foreign_key

                    # Model dictionary for migrations
                    model_dic = f"""{model} = {final_attrs}\n\n"""

                    # Update migrations content
                    migration_content += model_dic

                # Create the initial migration
                print('Creating the initial migration...')

                date = datetime.now().strftime("%m-%d-%Y")
                version = f'1-{date}'

                # Insert the initial migration to database
                new_db.create(table='migrations', data={'version':version,'current':True, 'date':date, 'comment':'The initial migration.'})
                
                # Create the migration file
                create_file(f'{app_path + url_div}migrations{url_div + version}.py', migration_content)
                # print(migration_content)

                # Print the message
                print('Database initialized successfully!')

            # Handle errors
            except NameError as err:
                print(err)

        # Exit the program
        exit()


    ##
    # @desc migrate_db method for migrating the database changes
    ##
    @click.command()
    def migrate_db():
        print('Work in progress!')

