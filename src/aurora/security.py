################
# Dependencies #
################
import re
import importlib
from datetime import datetime, timedelta
from typing import Union
from .helpers import route_url
from flask import make_response, jsonify, render_template, request as flask_request, abort as flask_abort, redirect as flask_redirect, session as flask_session
from werkzeug.security import check_password_hash, generate_password_hash

# Flask objects
request = flask_request
session = flask_session

# Fetch configuretion module
config = importlib.import_module('config')
debug = getattr(config, "DEBUG")
default_lang = getattr(config, "DEFAULT_LANG")
multi_lang = getattr(config, "MULTI_LANG")
languages = getattr(config, "LANGUAGES")

# Fetch apps module
apps_module = importlib.import_module('_apps')
apps = getattr(apps_module, "apps")


###################
# URL Redirecting #
###################
##
# @desc Redirects to HTTP error pages
# 
# @param {int} code -- The HTTP status code
#
# @return {object}
##
def abort(code:int=404):
    # Return result
    return flask_abort(status=code)


##
# @desc Redirects to relative URL
# 
# @param {str} url  -- The URL to redirect to
# @param {int} code -- The HTTP status code
#
# @return {object}
##
def redirect(url:str, code:int=302):
    # Return results
    return flask_redirect(location=url, code=code)


##
# @desc Redirects to app URL
# 
# @param {str} app        -- The app name
# @param {str} controller -- The app controller name
# @param {int} code       -- The HTTP status code
#
# @return object
##
def redirect_to(app:str, controller:str=None, code:int=302):
    # Fetch the route final url
    url = route_url(app, controller)
    
    # Return result
    return redirect(url=url, code=code)


##
# @desc Redirects not logged-in users
#
# @param {str}      app        -- The app name
# @param {str}      controller -- The app controller name
# @param {str|list} check      -- The session|cookie name(s) to check
#
# @var {str} next -- The next url
# 
# @return {object}
##
def login_required(app:str, controller:str=None, check:Union[str, list]='user'):
    def wrapper(inner):
        def decorator(*args, **kwargs):
            # Fetch the route final url
            url = route_url(app, controller)

            # Find next URL
            next = request.url.replace(request.url_root, '/')

            # check is of type str
            if type(check) is str:
                # Check cookie
                if check_cookie(check):
                    set_session(check, get_cookie(check))

                # User is logged-in
                if check_session(check):
                    return inner(*args, **kwargs)

            # check is of type list
            elif type(check) is list:
                for x in check:
                    # Check cookie
                    if check_cookie(x):
                        set_session(x, get_cookie(x))

                    # User is logged-in
                    if check_session(x):
                        return inner(*args, **kwargs)

            # User is not logged-in
            # Check the language
            if multi_lang:
                if check_session('active_lang'):
                    return redirect(f'''/{get_session('active_lang')}/{url}?next={next}''')

            return redirect(f'{url}?next={next}')

        return decorator
    return wrapper


##
# @desc Redirects logged-in users
#
# @param {str}      app        -- The app name
# @param {str}      controller -- The app controller name
# @param {str|list} check      -- The session|cookie name(s) to check
#
# @return {object}
##
def login_abort(app:str, controller:str=None, check:Union[str, list]='user'):
    def wrapper(inner):
        def decorator(*args, **kwargs):
            # Fetch the route final url
            url = route_url(app, controller)

            # check is of type str
            if type(check) is str:
                # Check cookie
                if check_cookie(check):
                    set_session(check, get_cookie(check))

                # User is logged-in
                if check_session(check):
                    return redirect(url)

            # check is of type list
            elif type(check) is list:
                for x in check:
                    # Check cookie
                    if check_cookie(x):
                        set_session(x, get_cookie(x))

                    # User is logged-in
                    if check_session(x):
                        return redirect(url)

            # User is not logged-in
            return inner(*args, **kwargs)

        return decorator
    return wrapper


####################
# Validating Users #
####################
##
# @desc Checks session for existence
# 
# @param {str} name -- Required session name
# 
# @return {bool}
##
def check_session(name:str):
    # Session exists
    if name in session:
        return True

    # Session not exists
    else:
        return False


##
# @desc Gets session
# 
# @param {str} name -- Required session name
# 
# @return {object}
##
def get_session(name:str):
    return session[name]


##
# @desc Sets session
# 
# @param {str} name  -- Required session name
# @param {str} value -- Required session value
##
def set_session(name:str, value:str):
    session[name] = value


##
# @desc Unset session
# 
# @param {str} name -- Required session name
##
def unset_session(name:str):
    session.pop(name, None)


##
# @desc Checks cookie for existence
# 
# @param {str} name -- Required cookie name
# 
# @return {bool}
##
def check_cookie(name:str):
    # Cookie exists
    if name in request.cookies:
        return True

    # Cookie not exists
    else:
        return False


##
# @desc Get cookie
# 
# @param {str} name -- Required cookie name
# 
# @return {object}
##
def get_cookie(name:str):
    return request.cookies.get(name)


##
# @desc Sets cookie
# 
# @param {str}  name  -- Required cookie name
# @param {str}  value -- Required cookie value
# @param {int}  days  -- Optional expiry days
# @param {dict} data  -- Optional data
# 
# @return {object}
##
def set_cookie(name:str, value:str, data:dict={}, days:int=30):
    # Check required params
    if not name and not value:
        # Produce error message
        error = 'Please provide the required parameters!'

        # Check debug mode
        if debug:
            # Raise error
            raise Exception(error)

        else:
            # Print error
            print(error)
            exit()

    # Check data
    if data:
        if data["type"] == "redirect":
            res = make_response(redirect(data["response"]))

        elif data["type"] == "render":
            res = make_response(render_template(data["response"]))

        elif data["type"] == "json":
            res = make_response(jsonify(data["response"]))

        elif data["type"] == "text":
            res = make_response(data["response"])

    # Create response
    else:
        res = make_response("Cookie set successfully!")

    # expires in 30 days
    expire = datetime.utcnow() + timedelta(days=days)

    # Set cookie
    res.set_cookie(name, value, expires=expire)

    # Return response
    return res


##
# @desc Unsets cookie
# 
# @param {str}  name -- Required cookie name
# @param {dict} data -- Optional data
##
def unset_cookie(name:str, data:dict={}):
    # Check required params
    if not name:
        # Produce error message
        error = 'Please provide the required parameters!'

        # Check debug mode
        if debug:
            # Raise error
            raise Exception(error)

        else:
            # Print error
            print(error)
            exit()

    # Check data
    if data:
        if data["type"] == "redirect":
            res = make_response(redirect(data["response"]))

        elif data["type"] == "render":
            res = make_response(render_template(data["response"]))

        elif data["type"] == "json":
            res = make_response(jsonify(data["response"]))

        elif data["type"] == "text":
            res = make_response(data["response"])

    else:
        res = make_response("Cookie unset successfully!")

    # unset cookie
    res.set_cookie(name, '', expires=0)

    # Return response
    return res


#####################
# Password Security #
#####################
##
# @desc Hashing password
# 
# @param {str} password -- The password to hash
#
# @return {str}
##
def hash_password(password):
    return generate_password_hash(password)


##
# @desc Validates a hashed password
# 
# @param {str} hashed_password    -- Hashed password from database
# @param {str} requested_password -- Requested password by the user
#
# @return {bool}
##
def validate_password(hashed_password, requested_password):
    # Valid password
    if check_password_hash(hashed_password, requested_password):
        return True

    # Invalid password
    else:
        return False


##
# @desc Checks a password strength
# 
# @param {str}  password  -- The password to validate
# @param {int}  length    -- The password minimum length
# @param {bool} digit     -- Check for digit?
# @param {bool} uppercase -- Check for uppercase?
# @param {bool} lowercase -- Check for lowercase?
# @param {bool} symbol    -- Check for symbol?
#
# @return dict
##
def password_strength(password:str, length:int=8, digit:bool=True, uppercase:bool=True, lowercase:bool=True, symbol:bool=True):
    """
        With all parameters provided,
        The password should:
        - Be greater than or equal to `length`
        - Contain one digit or more
        - Contain one uppercase letter or more
        - Contain one lowercase letter or more
        - Contain one symbol or more
    """

    # Check the length
    length = len(password) >= length

    # Check for digits
    digit = bool(re.search(r"\d", password)) if digit else True

    # Check for uppercase
    uppercase = bool(re.search(r"[A-Z]", password)) if uppercase else True

    # Check for lowercase
    lowercase = bool(re.search(r"[a-z]", password)) if lowercase else True

    # Check for symbols
    symbol = bool(re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password)) if symbol else True

    # Overall result
    result = length and digit and uppercase and lowercase and symbol

    # Return the collected result
    return {
        'result'    : result,
        'length'    : length,
        'digit'     : digit,
        'uppercase' : uppercase,
        'lowercase' : lowercase,
        'symbol'    : symbol,
    }


##############
# IP Methods #
##############
##
# @desc Returns the server IP
#
# @retun {str}
##
def server_ip():
    return request.remote_addr


##
# @desc Returns the client IP
# 
# @param {bool} strict -- If True, returns the client's public IP, not a private IP behind a proxy
#
# @retun {str}
##
def client_ip(strict:bool=True):
    # Client is behind a proxy (strict mod)
    if request.environ.get('HTTP_X_FORWARDED_FOR') and strict:
        return request.environ['HTTP_X_FORWARDED_FOR']
    
    # Client doesn't use proxy
    else:
        return request.environ['REMOTE_ADDR']


#################
# Other Methods #
#################
##
# @desc Finds active language
# 
# @var {str} active_lang -- The active language code
#
# @return {str}
##
def find_lang():
    path = request.path
    lang = path.split('/')[1]

    # Check multi language
    if multi_lang:
        # Check the language path
        if lang in languages:
            active_lang = lang
            LANGUAGE = '/' + active_lang
            set_session('active_lang', lang)

        elif check_cookie('active_lang'):
            active_lang = get_cookie('active_lang')
            LANGUAGE = '/' + active_lang
            set_session('active_lang', get_cookie('active_lang'))

        elif check_session('active_lang'):
            active_lang = get_session('active_lang')
            LANGUAGE = '/' + active_lang

        else:
            active_lang = default_lang
            LANGUAGE = '/' + active_lang
            set_session('active_lang', default_lang)

    else:
        active_lang = default_lang
        LANGUAGE = ''

    # Return result
    return {
        'active_language': active_lang,
        'LANGUAGE': LANGUAGE,
    }
