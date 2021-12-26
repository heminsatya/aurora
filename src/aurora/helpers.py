################
# Dependencies #
################
import os
import re
import string
import random
import shutil
from zipfile import ZipFile
from pathlib import Path


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
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


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
# @desc Convert named list into dictionary list, for PostgreSQL Database
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


#################
# File Handling #
#################
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
#
# @retun bool -- True (on success), False (on error)
##
def replace_file_string(file_path:str, old_str:str, new_str:str):
    # Read the file
    with open(file_path, 'r') as file :
        f = file.read()

    # Replace the string
    f = f.replace(old_str, new_str)

    # Write the file out again
    with open(file_path, 'w') as file:
        file.write(f)


##
# @desc Replace lines in a file contain a string with new line data
#
# @param file_path: str - The absolute file path
# @param old_line: str - The character to match in the line
# @param new_str: str - The new line data
#
# @retun bool -- True (on success), False (on error)
##
def replace_file_line(file_path:str, old_line:str, new_line:str):
    # Open file
    with open(file_path, 'r+') as f:
        
        # Read lines
        lines = f.readlines()
        
        # Set the position to the beginning of the file 
        f.seek(0)

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
# @desc Validates base url
#
# @param url: str - The app name
#
# @retun dict
##
def base_url(url:str):
    # Check required base URL
    if not url:
        return {
            'result': False, 
            'message': 'The base URL is required!'
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
            'message': 'The base URL is invalid.\nValid characters: a-z, -'
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
    regex = '^[a-z]+[a-z-<>:/]*$'

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
            'message': 'The controller URL is invalid.\nValid characters: a-z, -, /, <, :, >'
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

