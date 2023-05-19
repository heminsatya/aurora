################
# Dependencies #
################
import os
import re
import json
import string
import random
import shutil
import importlib
from zipfile import ZipFile
from pathlib import Path
import time
from datetime import datetime, timedelta


##########
# Aurora #
##########
##
# @desc Generates controller routes
# 
# @param {str}  controller -- The controller class name
# @param {str}  url        -- The controller url
# @param {list} methods    -- The controller REST methods
# 
# @return {tuple}
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
# @param {str} name -- The app name
# @param {str} url  -- The app base url
# 
# @return {tuple}
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
# @desc Checks if an app exists
# 
# @param {str} app -- The app name
#
# @var {list} apps -- The apps list
# 
# @return {dict}
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
# @param {str} url -- The app url
# 
# @return {bool}
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
# @desc Check if an controller name exists
# 
# @param {str} app        -- The app name
# @param {str} controller -- The controller name
#
# @var {list} controllers -- The controllers list
# 
# @return {dict}
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
            'message': f'- The "{app}" app doesn\'t have the "{controller}" controller!'
        }


##
# @desc Check if a controller url exists
# 
# @param {str} app -- The app name
# @param {str} url -- The controller url
# 
# @return {bool}
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
# @param {str} app        -- The app name
# @param {str} controller -- The app controller name
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


###############
# CLI Helpers #
###############
##
# @desc Validates app name
#
# @param {str} name -- The app name
#
# @retun {dict}
##
def app_name(name:str):
    # Check required app name
    if not name:
        return {
            'result': False, 
            'message': '- The app name is required!'
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
            'message': '- The app name is invalid!\n- Valid characters: a-z, _'
        }


##
# @desc Validates app url
#
# @param {str} url -- The app url
#
# @retun {dict}
##
def app_url(url:str):
    # Check required app URL
    if not url:
        return {
            'result': False, 
            'message': '- The app URL is required!'
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
            'message': '- The app URL is invalid!\n- Valid characters: a-z, -'
        }


##
# @desc Validates controller name
#
# @param {str} name -- The controller name
#
# @retun {dict}
##
def controller_name(name:str):
    # Check required controller name
    if not name:
        return {
            'result': False, 
            'message': '- The controller name is required!'
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
            'message': '- The controller name must be in "CamelCase" form with at least two "a-z" and "A-Z" characters!'
        }


##
# @desc Validates controller url
#
# @param {str} url -- The app name
#
# @retun {dict}
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
            'message': '- The controller URL is invalid!\n- Valid characters: a-z, 0-9, -, /, <, :, >'
        }


##
# @desc Validates controller methods
#
# @param {list} methods -- The controller methods
#
# @retun {dict}
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
                'message': '- Valid Methods: POST, GET, PUT, DELETE'
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
# @param {str} view -- The view name
#
# @retun {dict}
##
def view_name(view:str):
    # Check required base URL
    if not view:
        return {
            'result': False, 
            'message': '- The view is required!'
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
            'message': '- The view is invalid!\n- Valid characters: a-z, -, _'
        }


##
# @desc Validates model name
#
# @param {str} name -- The model name
#
# @retun {dict}
##
def model_name(name:str):
    # Check required model name
    if not name:
        return {
            'result': False, 
            'message': '- The model name is required!'
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
            'message': '- The model name must be in "CamelCase" form with at least two "a-z" and "A-Z" characters!'
        }


##
# @desc Validates form name
#
# @param {str} name -- The form name
#
# @retun {dict}
##
def form_name(name:str):
    # Check required form name
    if not name:
        return {
            'result': False, 
            'message': '- The form name is required!'
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
            'message': '- The form name must be in "CamelCase" form with at least two "a-z" and "A-Z" characters!'
        }


##
# @desc Validates database table names
#
# @param {str} name -- The app name
#
# @retun {dict}
##
def table_name(name:str):
    # Check required table name
    if not name:
        return {
            'result': False, 
            'message': '- The table name is required!'
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
            'message': '- Database table names must be in "snake_case" form with at least two a-z, _ characters!'
        }


##
# @desc Validates database column names
#
# @param {str} name -- The app name
#
# @retun {dict}
##
def column_name(name:str):
    # Check required column name
    if not name:
        return {
            'result': False, 
            'message': '- The column name is required!'
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
            'message': '- Database column names must be in "snake_case" form with at least two a-z, _ characters!'
        }


###################
# String Handling #
###################
##
# @desc Generates a random string
# 
# @param {int} size  -- The size of output (characters)
# @param {str} chars -- The type of characters
# 
# @return {str}
##
def random_string(size:int=8, chars:str=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


##
# @desc Converts CamelCase string to snake_case string
#
# @param {str} CamelCase - The string in CamelCase
#
# @retun {str}
##
def snake_case(CamelCase:str):
    result = ""

    result = re.sub(r'(?<!^)(?=[A-Z])', '_', CamelCase).lower()

    return result


##
# @desc Converts a text to snake_case string
#
# @param {str} text
#
# @retun {str}
##
def to_snake_case(text:str):
    result = ''
    underscore = False

    # Remove the spaces
    name = delete_chars(text, ' ')

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
# @desc Deletes the sequences of a character from a text.
#
# @param {str} text -- The text to format
# @param {str} char -- The character to delete in the text
#
# @retun {str}
##
def delete_chars(text:str, char:str):
    return re.sub(r'{}'.format(char), '', text)


##
# @desc Cleans keys for the WHERE clause for SQL Class
#
# @param {str} key - The key to clean
#
# @retun {str}
##
def clean_key(key:str):
    # Clean the key
    new_key = delete_chars(key, "'")
    new_key = delete_chars(new_key, '"')
    new_key = delete_chars(new_key, "`")

    # Return the new key
    return new_key


##
# @desc Removes HTML tags from a text
#
# @param {str} text -- The text to format
#
# @return {str}
##
def remove_html(text:str):
    regex = re.compile('<.*?>') 
    return re.sub(regex, '', text)


##
# @desc Returns a fixed sized text
#
# @param {str} text -- The text to format
# @param {int} num  -- The number of characters to retrn
#
# @return {str}
##
def fixed_chars(text:str, num:int):
    return text[:num]


##
# @desc Removes HTML tags from a text and returns a fixed sized text
#
# @param {str} text -- The text to format
# @param {int} num  -- The number of characters to retrn
#
# @return {str}
##
def clean_text(text:str, num:int):
    return fixed_chars(remove_html(text), num)


################
# JSON Helpers #
################
##
# @desc Checks if a text is in correct JSON format
# 
# @param {str} text -- The text to execute
# 
# @var {bool} result -- The execution result
#
# @retun {bool}
##
def is_json(text:str):
    result = True

    # Is JSON
    try:
        json.loads(text)

    # Is not JSON
    except ValueError as e:
        result = False

    # Return the result
    return result


##
# @desc Produces a dictionary from a json file
#
# @param {str} path -- The file path
# 
# @return {dict|bool}
##
def json_dict(path:str):
    # No file
    if not path:
        return False

    # Read file
    text = read_file(path)

    # Check file
    if text:
        # Convert to dict & return
        return json_eval(text)

    # File error
    else:
        return False


##
# @desc Evalutes a JSON object into python dictionary
#
# @param {str} text -- The JSON object
# 
# @return {dict}
##
def json_eval(text:str):
    return json.loads(text)


########################
# Collection Hendling  #
########################
##
# @desc Convert tuple list into dictionary list, for SQLite Database
#
# @param {object} cur -- database connection cursor
# @param {object} row -- database rows
#
# @var {dict} d -- The output dictionary
#
# @retun {dict}
##
def dict_factory(cur:object, row:object):
    d = {}

    for i, col in enumerate(cur.description):
        d[col[0]] = row[i]

    return d


##
# @desc Convert named list into dictionary list, for Postgres Database
#
# @param {list} cur -- a named list
#
# @var {list} translate -- a dictionary list
#
# @retun {list} (of dictionaries)
##
def real_dict(cur:list):
    translate = []

    for x in cur:
        translate.append(dict(x))

    return translate


##
# @desc Checks if there are duplicates in a list
#
# @param {list} ls -- The list to check
#
# @retun {bool}
##
def list_dup(ls:list):
    return len(ls) != len(set(ls))


##
# @desc Checks if there are duplicate values in a dictionary
#
# @param {dict} dt -- The dictionary to check
#
# @retun {bool}
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
# @param {str} path -- The absolute file path
#
# @retun {bool}
##
def file_exist(path:str):
    # File exists
    if os.path.exists(path):
        return True

    # File not exists
    else:
        return False


##
# @desc Validates file name
#
# @param {str} file_name -- The file name to check (without extension)
#
# @var {str} regex -- Regular expression
#
# @retun {bool}
##
def file_name(file_name:str):
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
# @param {str}  file_name -- The file full name (ex. 'example.py')
# @param {str}  extension -- The file extension (ex. '.py', '.*')
# @param {bool} safe      -- Safe character names (a-z, A-Z, _)
#
# @var {str} regex -- Regular expression
#
# @retun {bool}
##
def check_file(file_name:str, extension:str, safe:bool=True):
    # Check required files
    if not file_name or not extension:
        return False

    if extension == '.*':
        extension = '.[a-zA-Z]+'

    # Regular expression
    regex = f'^[a-zA-Z_]+[a-zA-Z0-9_]*\{extension}$' if safe else f'.*\{extension}$'

    # Valid name and extension
    if re.match(regex, file_name):
        return True

    # Invalid name or extension
    else:
        return False


##
# @desc Creates a file if not exists
#
# @param {str} file_path -- The absolute file path
# @param {str} content   -- The content of the file
#
# @retun {bool}
##
def create_file(file_path:str, content:str=''):
    # File not exists
    if not os.path.exists(file_path):
        # Create the file
        f = open(file_path, 'x')
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
# @param {str} file_path -- The absolute file path
# @param {str} content   -- The content of the file
#
# @retun {bool}
##
def write_file(file_path:str, content:str=''):
    # File already exists
    if os.path.exists(file_path):
        # Write to the file
        f = open(file_path, 'w')
        f.write(content)
        f.close()

        # Return result
        return True

    # File not exists
    else:
        # Return Result
        return False


##
# @desc Reads a file and returns its content if exists
#
# @param {str} file_path -- The absolute file path
#
# @retun {any}
##
def read_file(file_path:str):
    # File already exists
    if os.path.exists(file_path):
        # Read file
        with open(file_path, 'r') as file:
            f = file.read()

        # Return result
        return f

    # File not exists
    else:
        # Return Result
        return False


##
# @desc Copies a file to a new destination
#
# @param {str} src  -- The source file path
# @param {str} dist -- The destination file path
#
# @retun {bool}
##
def copy_file(src:str, dist:str):
    # Source file exists
    if os.path.exists(src):
        # Copy the source file to the destination file
        shutil.copyfile(src, dist)

        # Return result
        return True

    # Source file not exists
    else:
        # Return Result
        return False


##
# @desc Moves a file to a new destination
#
# @param {str} src  -- The source file path
# @param {str} dist -- The destination file path
#
# @retun {bool}
##
def move_file(src:str, dist:str):
    # Source file exists
    if os.path.exists(src):
        # Check the file
        if re.search('[.]', src) and re.search('[.]', dist):
            # Copy the source file to the destination file
            shutil.move(src, dist)

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
# @desc Renames a file if exists
#
# @param {str} src  -- The source file path
# @param {str} dist -- The destination file path
#
# @retun {bool}
##
def rename_file(src:str, dist:str):
    # Source file exists
    if os.path.exists(src):
        # Check the file
        if re.search('[.]', src) and re.search('[.]', dist):
            # Rename the source file to the destination file
            os.rename(src, dist)

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
# @desc Removes a file permanently if exists
#
# @param {str} file_path -- The absolute file path
#
# @retun {bool}
##
def delete_file(file_path:str):
    # File already exists
    if os.path.exists(file_path):
        # Remove the file
        os.remove(file_path)

        # Return result
        return True

    # File not exists
    else:
        # Return Result
        return False


##
# @desc unzips a zip file to a directory
#
# @param {str} file_path -- The absolute zip file path
# @param {str} dist_dir  -- The destination directory to unzip the file
#
# @retun {bool} -- True (on success), False (on error)
##
def unzip_file(file_path:str, dist_dir:str):
    with ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dist_dir)


##
# @desc Replaces strings in a file with new ones
#
# @param {str}  file_path -- The absolute file path
# @param {str}  old_str   -- The old string
# @param {str}  new_str   -- The new string
# @param {bool} regex     -- For replacing a regular expression
#
# @retun {bool} -- True (on success), False (on error)
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
# @desc Replaces lines in a file contain a string with new line data
#
# @param {str}  file_path -- The absolute file path
# @param {str}  old_line  -- The character to match in the line
# @param {str}  new_str   -- The new line data
# @param {bool} regex     -- For replacing a regular expression
#
# @retun {bool} -- True (on success), False (on error)
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

    # Close file
    return f.close()


##
# @desc Replaces multiple lines in a file between two strings with new data
#
# @param {str}  starting_str -- The starting string
# @param {str}  ending_str   -- The ending string
# @param {str}  replace_to   -- The new data to replace
#
# @retun {bool} -- True (on success), False (on error)
##
def replace_file_lines(file_path:str, starting_str, ending_str, replace_to):
    # Read the file
    content = read_file(file_path)

    # Write the file
    with open(file_path, 'w') as f:
        # Find lines
        replace_from = content[content.find(starting_str)+len(starting_str):content.rfind(ending_str)]

        # Replace lines
        content = content.replace(replace_from, replace_to)

        # Rewrite the file
        f.writelines(content)

    # Close the file
    return f.close()


######################
# Directory Handling #
######################
##
# @desc Checks if a directory exists
#
# @param {str} dir -- The directory string
#
# @retun {bool} -- True (directory exists), False (direcory does not exist)
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
# @param {str} dir -- The directory string
# 
# @var {list} dir_list -- Lists the direcotry sub direcories and files
#
# @retun {bool} -- True (directory is empty), False (direcory is not empty)
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
# @desc Creates a directory if not exists
#
# @param {str} dir -- The directory string
#
# @retun {bool} -- True (on success), False (on error)
##
def create_dir(dir:str):
    # Try to create the directory
    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
        return True
    
    # Handle errors
    except:
        return False


##
# @desc Renames a directory if exists
#
# @param {str} src  -- The absolute source path
# @param {str} dist -- The absolute destination path
#
# @retun bool
##
def rename_dir(src:str, dist:str):
    # Directory exists
    if dir_exist(src):
        # Rename directory
        os.rename(src, dist)

        # Return result
        return True

    # Directory not exists
    else:
        # Return Result
        return False


##
# @desc Removes a directory and all its files and sub-directories permanently
#
# @param {str} dir -- The directory string
#
# @retun {bool} -- True (on success), False (on error)
##
def delete_dir(dir:str):
    # Try to delete the directory
    try:
        shutil.rmtree(dir)
        return True
    
    # Handle errors
    except:
        return False


##
# @desc Calculates a directory size (in Bytes)
#
# @param {str} dir -- The directory string
#
# @retun {int|bool} -- int (on success), False (on error)
##
def dir_size(dir:str):
    # Check directory existance
    if not dir_exist(dir):
        return False

    # Default size
    size = 0

    # Find all items
    for item in os.listdir(dir):
        # List item
        items = os.path.join(dir, item)

        # File
        if os.path.isfile(items):
            # Update size
            size += os.path.getsize(items)

        # Folder
        elif os.path.isdir(items):
            # Update size
            size += dir_size(items)

    # Return calculated size
    return size


################
# Time Helpers #
################
##
# @desc Generates current time in milliseconds
#
# @retun {int}
##
def current_time():
    return round(time.time() * 1000)


##
# @desc Generates time in milliseconds from a date
#
# @param {str} date   -- The date string
# @param {str} format -- The date format
#
# @retun {int}
##
def generate_time(date, format='%Y-%m-%d %H:%M:%S'):
    # Clean the date
    date = date.replace('T', ' ')

    # Convert date to datetime
    date = datetime.strptime(date, format)

    # Return the result
    return round(date.timestamp() * 1000)


##
# @desc Creates a time in milliseconds from given parameters
#
# @param {int} seconds -- The seconds from or before the current time
# @param {int} minutes -- The minutes from or before the current time
# @param {int} hours   -- The hours from or before the current time
# @param {int} days    -- The days from or before the current time
# @param {int} weeks   -- The weeks from or before the current time
# @param {int} months  -- The months from or before the current time
# @param {int} years   -- The years from or before the current time
# 
# @retun {int|bool}
##
def create_time(seconds:int=0, minutes:int=0, hours:int=0, days:int=0, weeks:int=0, months:int=0, years:int=0):
    # Find today datetime
    today = datetime.now()

    # Check months & year
    if months or years:
        # Split date
        split_date = str(today).split('-')

        # Find year
        year  = int(split_date[0]) + years

        # Find month
        month = int(split_date[1]) + months

        # Update year
        year += month // 12

        # Update month
        month = month % 12

        # Check final month
        if month == 0:
            # Update month and year
            month = 12
            year -= 1

        # Check year
        if year not in range(1970, 2038):
            print('Warning! create_time() method can only create date from 1970, 2038!')
            return False

        # Stringify month
        if month >= 10: month = str(month)
        else:           month = '0' + str(month)

        # Stringify year
        year = str(year)

        # Generate the new date
        new_date = year + '-' + month + '-' + split_date[2]

        # Correct time range
        try:
            # Update today
            today = datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S.%f')

        # Wrong time range
        except:
            split_day = split_date[2].split(' ')

            # Go to the first day of the next month
            # Update day
            day = 1

            # Refine month & year formats
            year  = int(year)
            month = int(month)

            # Check month
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

            # Stringify day
            day = str(day)

            # Stringify month
            if month >= 10: month = str(month)
            else:           month = '0' + str(month)

            # Stringify year
            year = str(year)

            # Generate the new date
            new_date = year + '-' + month + '-' + day + ' ' + split_day[1]

            # Update today
            today = datetime.strptime(new_date, '%Y-%m-%d %H:%M:%S.%f')

    # Generate time delta
    delta = timedelta(
        seconds = seconds * -1,
        minutes = minutes * -1,
        hours = hours * -1,
        days = days * -1,
        weeks = weeks * -1
    )

    # Generate the date without months & years
    final_date = str(today - delta)

    # Convert the date into milliseconds
    result = generate_time(date=final_date, format='%Y-%m-%d %H:%M:%S.%f')

    # Return the result
    return result


##
# @desc Generates the current date
# 
# @param {str} format -- The date format
#
# @retun {str}
##
def current_date(format: str = '%Y-%m-%d %H:%M:%S'):
    # Return the result
    return datetime.fromtimestamp(round(current_time() / 1000.0)).strftime(format)


##
# @desc Generates datetime from a time in milliseconds
# 
# @param {int} time_ms -- The time in milliseconds
# @param {str} format  -- The date format
#
# @retun {str}
##
def generate_date(time_ms: int, format: str = '%Y-%m-%d %H:%M:%S'):
    # Return the result
    return datetime.fromtimestamp(round(time_ms / 1000.0)).strftime(format)


##
# @desc Creates datetime from given parameters
# 
# @param {int} seconds -- The seconds from or before the current time
# @param {int} minutes -- The minutes from or before the current time
# @param {int} hours   -- The hours from or before the current time
# @param {int} days    -- The days from or before the current time
# @param {int} weeks   -- The weeks from or before the current time
# @param {int} months  -- The months from or before the current time
# @param {int} years   -- The years from or before the current time
# @param {str} format  -- The date format
#
# @retun {int|bool}
##
def create_date(seconds:int=0, minutes:int=0, hours:int=0, days:int=0, weeks:int=0, months:int=0, years:int=0, format: str = '%Y-%m-%d %H:%M:%S'):
    # Return the result
    return generate_date(time_ms=create_time(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks, months=months, years=years), format=format)


##
# @desc Returns week number of a time (in milliseconds) or a date, counting from 1
# 
# @param {int|str} time      -- The time (or date)
# @param {int}     first_day -- The first day of week (Sunday|Monday)
# @param {str}     format    -- The date format if time is date
#
# @retun {int}
##
def week_number(time, first_day='Sunday', format='%Y-%m-%d'):
    # Generates date
    if isinstance(time, int):
        date = datetime.strptime(generate_date(time, format), format)
    else:
        date = datetime.strptime(time, format)

    # Sunday as the first day of the week
    if first_day == 'Sunday':
        week_format = '%U'

    # Monday as the first day of the week
    elif first_day == 'Monday':
        week_format = '%W'

    week = datetime.date(date).strftime(week_format)

    # Return week number
    return int(week)


##
# @desc Returns seconds difference between two times (in milliseconds) or dates
# 
# @param {int|str} time_one -- The first time (or date)
# @param {int|str} time_two -- The second time (or date)
# @param {str}     format   -- The date format if times are date
#
# @retun {int}
##
def delta_seconds(time_one, time_two, format='%Y-%m-%d %H:%M:%S'):
    # Generates dates
    if isinstance(time_one, int):
        date_one = datetime.strptime(generate_date(time_one, format), format)
        date_two = datetime.strptime(generate_date(time_two, format), format)
    else:
        date_one = datetime.strptime(time_one, format)
        date_two = datetime.strptime(time_two, format)

    # Find dates delta
    delta = date_one - date_two

    # Return delta seconds
    return round(delta.total_seconds())


##
# @desc Returns days difference between two times (in milliseconds) or dates
# 
# @param {int|str} time_one -- The first time (or date)
# @param {int|str} time_two -- The second time (or date)
# @param {str}     format   -- The date format if times are date
#
# @retun {int}
##
def delta_days(time_one, time_two, format='%Y-%m-%d'):
    # Generates dates
    if isinstance(time_one, int):
        date_one = datetime.strptime(generate_date(time_one, format), format)
        date_two = datetime.strptime(generate_date(time_two, format), format)
    else:
        date_one = datetime.strptime(time_one, format)
        date_two = datetime.strptime(time_two, format)

    # Find dates delta
    delta = date_one - date_two

    # Return delta days
    return delta.days


##
# @desc Returns weeks difference between two times (in milliseconds) or dates
# 
# @param {int|str} time_one  -- The first time (or date)
# @param {int|str} time_two  -- The second time (or date)
# @param {str}     first_day -- The first day of week (Sunday|Monday)
# @param {str}     format    -- The date format if times are date
#
# @retun {int}
##
def delta_weeks(time_one, time_two, first_day='Sunday', format='%Y-%m-%d'):
    # Generates dates
    if isinstance(time_one, int):
        date_one = datetime.strptime(generate_date(time_one, format), format)
        date_two = datetime.strptime(generate_date(time_two, format), format)
    else:
        date_one = datetime.strptime(time_one, format)
        date_two = datetime.strptime(time_two, format)

    # Find dates delta
    # Sunday
    if first_day == 'Sunday':
        if date_one.weekday() + 1 == 7: weekday = 0
        else: weekday = date_one.weekday() + 1
        delta_one = (date_one - timedelta(weekday))

        if date_two.weekday() + 1 == 7: weekday = 0
        else: weekday = date_two.weekday() + 1
        delta_two = (date_two - timedelta(weekday))

    # Monday
    elif first_day == 'Monday':
        delta_one = (date_one - timedelta(date_one.weekday()))
        delta_two = (date_two - timedelta(date_two.weekday()))

    # Find week delta
    delta = int((delta_one - delta_two).days / 7)
                
    # Return week delta
    return delta


##
# @desc Returns months difference between two times (in milliseconds) or dates
# 
# @param {int|str} time_one -- The first time (or date)
# @param {int|str} time_two -- The second time (or date)
# @param {str}     format   -- The date format if times are date
#
# @retun {int}
##
def delta_months(time_one, time_two, format='%Y-%m-%d'):
    # Generates dates
    if isinstance(time_one, int):
        date_one = datetime.strptime(generate_date(time_one, format), format)
        date_two = datetime.strptime(generate_date(time_two, format), format)
    else:
        date_one = datetime.strptime(time_one, format)
        date_two = datetime.strptime(time_two, format)

    # Find dates delta
    delta = (date_one.year - date_two.year) * 12 + date_one.month - date_two.month

    # Return delta months
    return delta


##
# @desc Returns years difference between two times (in milliseconds) or dates
# 
# @param {int|str} time_one -- The first time (or date)
# @param {int|str} time_two -- The second time (or date)
# @param {str}     format   -- The date format if times are date
#
# @retun {int}
##
def delta_years(time_one, time_two, format='%Y-%m-%d'):
    # Generates dates
    if isinstance(time_one, int):
        date_one = datetime.strptime(generate_date(time_one, format), format)
        date_two = datetime.strptime(generate_date(time_two, format), format)
    else:
        date_one = datetime.strptime(time_one, format)
        date_two = datetime.strptime(time_two, format)

    # Find dates delta
    delta = date_one.year - date_two.year

    # Return delta years
    return delta
