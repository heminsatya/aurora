################
# Dependencies #
################
import importlib
from os import replace
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


##
# @desc Redirects to HTTP error pages
# 
# @param code: int - HTTP status code
#
# @return object
##
def abort(code:int=404):
    # Return result
    return flask_abort(status=code)


##
# @desc Redirects to relative URL
# 
# @param url: str
#
# @return object
##
def redirect(url:str, code:int=302):
    # Return results
    return flask_redirect(location=url, code=code)


##
# @desc Redirects to app URL
# 
# @param app: str - The app name
# @param controller: str - The app controller name
#
# @return object
##
def redirect_to(app:str, controller:str=None, code:int=302):
    # Fetch the route final url
    url = route_url(app, controller)
    
    # Return result
    return redirect(url=url, code=code)


##
# @desc Checks session for existence
# 
# @param name: str -- *Required session name
# 
# @return bool
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
# @param name: str -- *Required session name
# 
# @return object
##
def get_session(name:str):
    return session[name]


##
# @desc Sets session
# 
# @param name: str -- *Required session name
# @param value: str -- *Required session value
##
def set_session(name:str, value:str):
    session[name] = value


##
# @desc Unset session
# 
# @param name: str -- *Required session name
##
def unset_session(name:str):
    session.pop(name, None)


##
# @desc Checks cookie for existence
# 
# @param name: str -- *Required cookie name
# 
# @return bool
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
# @param name: str -- *Required cookie name
# 
# @return object
##
def get_cookie(name:str):
    return request.cookies.get(name)


##
# @desc Sets cookie
# 
# @param name: str -- *Required cookie name
# @param value: str -- *Required cookie value
# @param days: int -- Optional expiry days
# @param data: dictionary -- Optional data
# 
# @return object
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
# @param name: str -- *Required cookie name
# @param data: dictionary -- Optional data
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


##
# @desc Finds active language
# 
# @var active_lang: str - The active language code
#
# @return str
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


##
# @desc Redirects not logged-in users
#
# @param url: str -- *Required url for users app
#
# @var next: str -- The next url
# 
# @return object
##
def login_required(app:str, controller:str=None, check:Union[str, list]='user'):

    # Fetch the route final url
    url = route_url(app, controller)

    def wrapper(inner):
        def decorator(*args, **kwargs):
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
# @param url: str -- *Required url for app
#
# @return object
##
def login_abort(app:str, controller:str=None, check:Union[str, list]='user'):

    # Fetch the route final url
    url = route_url(app, controller)

    def wrapper(inner):
        def decorator(*args, **kwargs):
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


##
# @desc Hashing password
# 
# @param password: str
#
# @return str
##
def hash_password(password):
    return generate_password_hash(password)


##
# @desc Check hashed password with requested password
# 
# @param hashed_password: str -- Hashed password from database
# @param requested_password: str -- Requested password by the user
#
# @return bool
##
def check_password(hashed_password, requested_password):
    # Valid password
    if check_password_hash(hashed_password, requested_password):
        return True

    # Invalid password
    else:
        return False
