################
# Dependencies #
################
import os
import re
import string
import random
import shutil
import importlib
from zipfile import ZipFile
from pathlib import Path


##########
# Aurora #
##########
##
# @desc Generates controller routes
# 
# @param controller: str -- The controller class name
# @param url: str -- The controller url
# @param methods: list -- The controller REST methods
# 
# @return tuple
##
def controller(name:str, url:str='', methods:list=['GET']):
    # Check required params
    if not name:
        # Raise error
        raise Exception("You must provide the required parameters: ['name']")

    # Check controller name
    if not controller_name(name)['result']:
        # Raise error
        raise Exception(controller_name(name)['message'])

    # Check controller url
    if url and not controller_url(url)['result']:
        # Raise error
        raise Exception(controller_url(url)['message'])

    # Check controller methods
    if  not controller_methods(methods)['result']:
        # Raise error
        raise Exception(controller_methods(methods)['message'])

    return (name, url, methods)


##
# @desc Generates app route
# 
# @param name: str -- The app name
# @param url: str -- The app base url
# 
# @return tuple
##
def app(name:str, url:str):
    # Check required params
    if not name or not url:
        # Raise error
        raise Exception("You must provide the required parameters: ['name', 'url']")

    # Check app name
    if not app_name(name)['result']:
        # Raise error
        raise Exception(app_name(name)['message'])

    # Check app url
    if not app_url(url)['result']:
        # Raise error
        raise Exception(app_url(url)['message'])

    return (name, url)


##
# @desc Check if an app exists
# 
# @param app: str -- The app name
# @param apps: list -- The apps list
# 
# @return dict
##
def app_exists(app:str):
    # Apps info
    apps_module = importlib.import_module(f'_apps')
    apps = getattr(apps_module, 'apps')

    exists = False
    url = ''
    while True:
        i = 0
        for route in apps:
            # App exists
            if app == route[0]:
                url = route[1]
                exists = True
                break

            i += 1

        break

    # App exists
    if exists:
        return {
            'result': True, 
            'url': f'{url}'
        }

    # App not exists
    else:
        return {
            'result': False, 
            'message': f'The "{app}" app doesn\'t exist!'
        }


##
# @desc Check if an app url exists
# 
# @param url: str -- The app url
# 
# @return bool
##
def app_url_exists(url:str):
    # Apps info
    apps_module = importlib.import_module(f'_apps')
    apps = getattr(apps_module, 'apps')

    exists = False
    while True:
        i = 0
        for route in apps:
            # App url exists
            if url == route[1]:
                exists = True
                break

            i += 1

        break

    # App url exists
    if exists:
        return True

    # App url not exists
    else:
        return False


##
# @desc Check if an controller exists
# 
# @param app: str -- The app name
# @param controller: str -- The controller name
# @param controller: list -- The controllers list
# 
# @return dict
##
def controller_exists(app:str, controller:str):
    # Controllers info
    controllers_module = importlib.import_module(f'controllers.{app}._controllers')
    controllers = getattr(controllers_module, 'controllers')

    exists = False
    url = ''
    while True:
        i = 0
        for route in controllers:
            # App exists
            if controller == route[0]:
                url = route[1]
                exists = True
                break

            i += 1

        break

    # App exists
    if exists:
        return {
            'result': True, 
            'url': f'{url}'
        }

    # App not exists
    else:
        return {
            'result': False, 
            'message': f'The "{app}" app doesn\'t have the "{controller}" controller!'
        }


##
# @desc Check if an app url exists
# 
# @param app: str -- The app name
# @param url: str -- The app url
# 
# @return dict
##
def controller_url_exists(app:str, url:str=''):
    # Controllers info
    controllers_module = importlib.import_module(f'controllers.{app}._controllers')
    controllers = getattr(controllers_module, 'controllers')

    exists = False
    while True:
        i = 0
        for route in controllers:
            # Controller url exists
            if url == route[1]:
                exists = True
                break

            i += 1

        break

    # Controller url exists
    if exists:
        return True

    # Controller url not exists
    else:
        return False


##
# @desc Produces the final url for a route (app url + controller url)
# 
# @param app: str - The app name
# @param controller: str - The app controller name
#
# @return object
##
def route_url(app:str, controller:str=None):
    # Apps info
    apps_module = importlib.import_module(f'_apps')
    apps = getattr(apps_module, 'apps')

    app_url = ''

    # App not exists
    if not app_exists(app)['result']:
        # Raise error
        raise Exception(app_exists(app)['message'])

    # App exists
    else:
        app_url = app_exists(app)['url']

    # Controller inserted
    if controller:
        # Controller not exists
        if not controller_exists(app, controller)['result']:
            # Raise error
            raise Exception(controller_exists(app, controller)['message'])

        # Controller exists
        else:
            controller_url = controller_exists(app, controller)['url']

        url = f'/{app_url}/{controller_url}/'

    # Controller not inserted
    else:
        url = f'/{app_url}/'

    return url


###################
# String Handling #
###################
##
# @desc Generates random string
# 
# @param [size]: int -- The size of output (characters)
# @param [chars]: str -- The type of characters
# 
# @return str
##
def random_string(size:int=8, chars:str=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


##
# @desc Converts CamelCase to snake_case
#
# @param name: str - The name in CamelCase
#
# @retun str
##
def snake_case(name:str):
    result = ""

    result = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    return result


##
# @desc Converts string to snake_case
#
# @param name: str
#
# @retun str
##
def to_snake_case(name:str):
    result = ''
    underscore = False

    # Remove the spaces
    name = delete_chars(name, ' ')

    # Loop the name characters
    for i in range(len(name)):
        
        # Check if the next character is underscore
        if i < len(name) - 1:
            underscore = name[i + 1] == "_" or name[i + 1].isupper()

        # Ignore duplicated underscores
        if name[i] == "_" and underscore:
            continue

        # Accept single underscores
        elif name[i] == "_":
            result += "_"

        # Convert uppercase characters
        elif name[i].isupper():
            result += "_" + name[i].lower()

        # Accept other characters
        else:
            result += name[i]

    # Remove first character underscore
    if result[0] == "_":
        result = result[1:]

    # Return converted result
    return result


##
# @desc Delete characters from a string
#
# @param string: str - The string to format
# @param char: str - The character to delete in the string
#
# @retun str
##
def delete_chars(string:str, char:str):
    return re.sub(r'{}'.format(char), '', string)


################
# Collections  #
################
##
# @desc Convert tuple list into dictionary list, for SQLite Database
#
# @param cur: object - database connection cursor
# @param row: object - database rows
#
# @var d: dict
#
# @retun dict
##
def dict_factory(cur:object, row:object):
    d = {}

    for i, col in enumerate(cur.description):
        d[col[0]] = row[i]

    return d


##
# @desc Convert named list into dictionary list, for Postgres Database
#
# @param cur: list - a named list
#
# @var translate: list - a dictionary list
#
# @retun list (of dictionaries)
##
def real_dict(cur:list):
    translate = []

    for x in cur:
        translate.append(dict(x))

    return translate


##
# @desc Checks if there are duplicates in a list
#
# @param ls: list
#
# @retun bool
##
def list_dup(ls:list):
    return len(ls) != len(set(ls))


##
# @desc Checks if there are duplicate values in a dictionary
#
# @param dt: dict
#
# @retun bool
##
def dict_dup_val(dt:dict):
    new_dt = {}

    for key, value in dt.items():
        new_dt.setdefault(value, set()).add(key)

    if [key for key, values in new_dt.items() if len(values) > 1]:
        return True
    else:
        return False


#################
# File Handling #
#################
##
# @desc Checks if a file exists
#
# @param file: str - The absolute file path
#
# @retun bool
##
def file_exist(file:str):
    # File exists
    if os.path.exists(file):
        return True

    # File not exists
    else:
        return False


##
# @desc Validates file name
#
# @param file_name: str - The file name to check
#
# @var regex: str - Regular expression
#
# @retun bool
##
def check_name(file_name:str):
    # Check required files
    if not file_name:
        return False

    # Regular expression
    regex = f'^[a-zA-Z]+[a-zA-Z_-]*$'

    # Valid name
    if re.match(regex, file_name):
        return True

    # Invalid name
    else:
        return False


##
# @desc Validates file name and extension
#
# @param src: str - The source file path (ex. 'example.py')
# @param extension: str - The file extension (ex. '.py', '.*')
# @param safe: bool - Safe character names (a-z, A-Z, _)
#
# @var regex: str - Regular expression
#
# @retun bool
##
def check_file(src:str, extension:str, safe:bool=True):
    # Check required files
    if not src or not extension:
        return False

    if extension == '.*':
        extension = '.[a-zA-Z]+'

    # Regular expression
    regex = f'^[a-zA-Z_]+[a-zA-Z0-9_]*\{extension}$' if safe else f'.*\{extension}$'

    # Valid name and extension
    if re.match(regex, src):
        return True

    # Invalid name or extension
    else:
        return False


##
# @desc Creates a file if not exists
#
# @param file: str - The absolute file path
# @param content: str - The content of the file
#
# @retun bool
##
def create_file(file:str, content:str=''):
    # File not exists
    if not os.path.exists(file):
        # Create the file
        f = open(file, 'x')
        f.write(content)
        f.close()

        # Return result
        return True

    # File already exists
    else:
        # Return Result
        return False


##
# @desc Writes to a file if exists
#
# @param file: str - The absolute file path
# @param content: str - The content of the file
#
# @retun bool
##
def write_file(file:str, content:str=''):
    # File already exists
    if os.path.exists(file):
        # Write to the file
        f = open(file, 'w')
        f.write(content)
        f.close()

        # Return result
        return True

    # File not exists
    else:
        # Return Result
        return False


##
# @desc Writes to a file if exists
#
# @param src: str - The source file path
# @param dst: str - The destination file path
#
# @retun bool
##
def copy_file(src:str, dst:str):
    # Source file exists
    if os.path.exists(src):
        # Copy the source file to the destination file
        shutil.copyfile(src, dst)

        # Return result
        return True

    # Source file not exists
    else:
        # Return Result
        return False


##
# @desc Writes to a file if exists
#
# @param src: str - The absolute source path
# @param dst: str - The absolute destination path
#
# @retun bool
##
def move_file(src:str, dst:str):
    # Source file exists
    if os.path.exists(src):
        # Check the file
        if re.search('[.]', src) and re.search('[.]', dst):
            # Copy the source file to the destination file
            shutil.move(src, dst)

            # Return result
            return True

        # Missing extension
        else:
            # Return Result
            return False

    # Source file not exists
    else:
        # Return Result
        return False


##
# @desc Writes to a file if exists
#
# @param src: str - The absolute source path
# @param dst: str - The absolute destination path
#
# @retun bool
##
def rename_file(src:str, dst:str):
    # Source file exists
    if os.path.exists(src):
        # Check the file
        if re.search('[.]', src) and re.search('[.]', dst):
            # Rename the source file to the destination file
            os.rename(src, dst)

            # Return result
            return True

        # Missing extension
        else:
            # Return Result
            return False

    # Source file not exists
    else:
        # Return Result
        return False


##
# @desc Removes a file if exists
#
# @param file: str - The absolute file path
#
# @retun bool
##
def delete_file(file:str):
    # File already exists
    if os.path.exists(file):
        # Remove the file
        os.remove(file)

        # Return result
        return True

    # File not exists
    else:
        # Return Result
        return False


##
# @descunzips a file to a directory
#
# @param file_path: str - The absolute zip file path
# @param dest_dir: str - The destination directory to unzip the file
#
# @retun bool -- True (on success), False (on error)
##
def unzip_file(file_path:str, dest_dir:str):
    with ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)


##
# @desc Replace strings in a file with new ones
#
# @param file_path: str - The absolute file path
# @param old_str: str - The old string
# @param new_str: str - The new string
# @param regex: bool - For replacing a regular expression
#
# @retun bool -- True (on success), False (on error)
##
def replace_file_string(file_path:str, old_str:str, new_str:str, regex:bool=False):
    # Read the file
    with open(file_path, 'r') as file :
        f = file.read()

    # Replace regular expression
    if regex:
        f = re.sub(old_str, new_str, f, flags = re.M)
    
    # Replace string
    else:
        f = f.replace(old_str, new_str)

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(f)

    return file.close()


##
# @desc Replace lines in a file contain a string with new line data
#
# @param file_path: str - The absolute file path
# @param old_line: str - The character to match in the line
# @param new_str: str - The new line data
# @param regex: bool - For replacing a regular expression
#
# @retun bool -- True (on success), False (on error)
##
def replace_file_line(file_path:str, old_line:str, new_line:str, regex:bool=False):
    # Open file
    with open(file_path, 'r+') as f:
        
        # Read lines
        lines = f.readlines()
        
        # Set the position to the beginning of the file 
        f.seek(0)

        # Replace regular expression
        if regex:
            # Loop the lines
            for line in lines:
                # Replace old lines
                if re.match(old_line, line):
                    f.write(new_line)

                # Write other lines
                else:
                    f.write(line)
        
        # Replace string
        else:
            # Loop the lines
            for line in lines:
                # Replace old lines
                if old_line in line:
                    f.write(new_line)

                # Write other lines
                else:
                    f.write(line)

        # Resize the file to the current file stream position
        f.truncate()

    return f.close()


######################
# Directory Handling #
######################
##
# @desc Checks if a directory exists
#
# @param dir: str - The directory string
#
# @retun bool -- True (directory exists), False (direcory does not exist)
##
def dir_exist(dir:str):
    # Directory exists
    if os.path.isdir(dir):
        return True

    # Directory doesn't exist 
    else:
        return False


##
# @desc Checks if a directory is empty
#
# @param dir: str - The directory string
# 
# @var dir_list: list - Lists the direcotry sub direcories and files
#
# @retun bool -- True (directory is empty), False (direcory is not empty)
##
def dir_empty(dir:str):
    # Directories list
    dir_list = os.listdir(dir)

    # Directory is empty
    if len(dir_list) == 0:
        return True

    # Directory is not empty
    else:    
        return False


##
# @desc Create a directory if not exists
#
# @param dir: str - The directory string
#
# @retun bool -- True (on success), False (on error)
##
def make_dir(dir:str):
    # Try to create the directory
    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
        return True
    
    # Handle errors
    except:
        return False


##
# @desc removes a directory and all its contents
#
# @param dir: str - The directory string
#
# @retun bool -- True (on success), False (on error)
##
def delete_dir(dir:str):
    # Try to create the directory
    try:
        shutil.rmtree(dir)
        return True
    
    # Handle errors
    except:
        return False


#################
# CLI Helpers #
#################
##
# @desc Validates app name
#
# @param name: str - The app name
#
# @retun dict
##
def app_name(name:str):
    # Check required app name
    if not name:
        return {
            'result': False, 
            'message': 'The app name is required!'
        }

    # Regular expression
    regex = '^[a-z_]+$'

    # Valid name
    if re.match(regex, name):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid name
    else:
        return {
            'result': False, 
            'message': 'The app name is invalid.\nValid characters: a-z, _'
        }


##
# @desc Validates app url
#
# @param url: str - The app url
#
# @retun dict
##
def app_url(url:str):
    # Check required app URL
    if not url:
        return {
            'result': False, 
            'message': 'The app URL is required!'
        }

    # Regular expression
    regex = '^[a-z-]+$'

    # Valid URL
    if re.match(regex, url):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid URL
    else:
        return {
            'result': False, 
            'message': 'The app URL is invalid.\nValid characters: a-z, -'
        }


##
# @desc Validates controller name
#
# @param name: str - The controller name
#
# @retun dict
##
def controller_name(name:str):
    # Check required controller name
    if not name:
        return {
            'result': False, 
            'message': 'The controller name is required!'
        }

    # Regular expression
    regex = '^(?:[A-Z][a-z]+)+$'

    # Valid name
    if re.match(regex, name):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid name
    else:
        return {
            'result': False, 
            'message': 'The controller name must be in "CamelCase" form with at least two "a-z" and "A-Z" characters.'
        }


##
# @desc Validates controller url
#
# @param url: str - The app name
#
# @retun dict
##
def controller_url(url:str):
    # Optional base URL
    if not url:
        return {
            'result': True, 
            'message': ''
        }

    # Regular expression
    regex = '^[a-z0-9<]+[a-z0-9-<>:/]*$'

    # Valid URL
    if re.match(regex, url):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid URL
    else:
        return {
            'result': False, 
            'message': 'The controller URL is invalid.\nValid characters: a-z, 0-9, -, /, <, :, >'
        }


##
# @desc Validates controller methods
#
# @param methods: list - The controller methods
#
# @retun dict
##
def controller_methods(methods:list):
    # Optional methods
    if not methods:
        return {
            'result': True, 
            'message': ''
        }

    # Valid methods
    valid_methods = ['POST', 'PUT', 'GET', 'DELETE']

    # Validate methods
    for method in methods:
        # Invalid methods
        if not method.upper() in valid_methods:
            return {
                'result': False, 
                'message': 'Valid Methods: POST, GET, PUT, DELETE'
            }

        # Valid name
        else:
            return {
                'result': True, 
                'message': ''
            }


##
# @desc Validates view name
#
# @param view: str - The view name
#
# @retun dict
##
def view_name(view:str):
    # Check required base URL
    if not view:
        return {
            'result': False, 
            'message': 'The view is required!'
        }

    # Regular expression
    regex = '^[a-z-_]+$'

    # Valid view
    if re.match(regex, view):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid view
    else:
        return {
            'result': False, 
            'message': 'The view is invalid.\nValid characters: a-z, -, _'
        }


##
# @desc Validates model name
#
# @param name: str - The model name
#
# @retun dict
##
def model_name(name:str):
    # Check required model name
    if not name:
        return {
            'result': False, 
            'message': 'The model name is required!'
        }

    # Regular expression
    regex = '^(?:[A-Z][a-z]+)+$'

    # Valid name
    if re.match(regex, name):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid name
    else:
        return {
            'result': False, 
            'message': 'The model name must be in "CamelCase" form with at least two "a-z" and "A-Z" characters.'
        }


##
# @desc Validates form name
#
# @param name: str - The form name
#
# @retun dict
##
def form_name(name:str):
    # Check required form name
    if not name:
        return {
            'result': False, 
            'message': 'The form name is required!'
        }

    # Regular expression
    regex = '^(?:[A-Z][a-z]+)+$'

    # Valid name
    if re.match(regex, name):
        return {
            'result': True, 
            'message': ''
        }

    # Invalid name
    else:
        return {
            'result': False, 
            'message': 'The form name must be in "CamelCase" form with at least two "a-z" and "A-Z" characters.'
        }


##
# @desc Validates database table names
#
# @param name: str - The app name
#
# @retun dict
##
def table_name(name:str):
    # Check required table name
    if not name:
        return {
            'result': False, 
            'message': 'The table name is required!'
        }

    # Regular expression
    regex = '^[a-z_]+$'

    # Valid name
    if re.match(regex, name) and name == to_snake_case(name) and len(name) >= 2:
        return {
            'result': True, 
            'message': ''
        }

    # Invalid name
    else:
        return {
            'result': False, 
            'message': 'Database table names must be in "snake_case" form with at least two a-z, _ characters.'
        }


##
# @desc Validates database column names
#
# @param name: str - The app name
#
# @retun dict
##
def column_name(name:str):
    # Check required column name
    if not name:
        return {
            'result': False, 
            'message': 'The column name is required!'
        }

    # Regular expression
    regex = '^[a-z_]+$'

    # Valid name
    if re.match(regex, name) and name == to_snake_case(name) and len(name) >= 2:
        return {
            'result': True, 
            'message': ''
        }

    # Invalid name
    else:
        return {
            'result': False, 
            'message': 'Database column names must be in "snake_case" form with at least two a-z, _ characters.'
        }

