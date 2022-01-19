################
# Dependencies #
################
import importlib
from os import replace
from datetime import datetime, timedelta
from flask import session, request, make_response, jsonify, render_template
from werkzeug.security import check_password_hash, generate_password_hash

# Fetch configuretion module
config = importlib.import_module('config')
debug = getattr(config, "DEBUG")

# Fetch apps module
apps_module = importlib.import_module('_apps')
apps = getattr(apps_module, "apps")


##
# @desc Redirect to HTTP error pages
# 
# @param code: int - HTTP status code
#
# @return object
##
def abort(code:int=404):
    # Dependencies
    from flask import abort

    # Return result
    return abort(code=code)


##
# @desc Redirecty to relative URL
# 
# @param url: str
#
# @return object
##
def redirect(url:str):
    # Dependencies
    from flask import redirect

    # Return results
    return redirect(location=url, code=302)


##
# @desc Redirecty to app URL
# 
# @param app: str - The app name
# @param controller: str - The app controller name
#
# @return object
##
def redirect_to(app:str, controller:str=None):
    # Check app name
    if not app in apps:
        # Produce error message
        error = f'The "{app}" app doesn\'t exist!'

        # Check debug mode
        if debug:
            # Raise error
            raise Exception(error)

        else:
            # Print error
            print(error)
            exit()

    # Controller inserted
    if controller:
        # Controllers info
        module = importlib.import_module(f'controllers.{app}._controllers')
        controllers = getattr(module, 'controllers')

        # Check controller existence
        controller_exists = True
        while controller_exists:
            i = 0
            for ctrl in controllers:
                # Controller exists
                if controller in ctrl:
                    break
                
                i += 1

            controller_exists = False
            break

        if controller_exists:
            # Produce error message
            error = f'The "{app}" app doesn\'t have the "{controller}" controller!'

            # Check debug mode
            if debug:
                # Raise error
                raise Exception(error)

            else:
                # Print error
                print(error)
                exit()

        url = f'/{apps[app]}/{controllers[i][1]}/'

    # Controller not inserted
    else:
        url = f'/{apps[app]}/'
    
    # Return result
    return redirect(url=url)


##
# @desc Set session
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
# @desc Check session for existence
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
# @desc Set cookie
# 
# @param name: str -- *Required cookie name
# @param value: str -- *Required cookie value
# @param days: int -- Optional expiry days
# @param data: dictionary -- Optional data
# 
# @return object
##
def set_cookie(name:str, value:str, days:int=30, data:dict={}):
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
            res = make_response(redirect(data["next"]))

        elif data["type"] == "render":
            res = make_response(render_template(data["next"]))

        elif data["type"] == "json":
            res = make_response(jsonify(data["next"]))

        elif data["type"] == "text":
            res = make_response(data["next"])

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
# @desc Unset cookie
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
            res = make_response(redirect(data["next"]))

        elif data["type"] == "render":
            res = make_response(render_template(data["next"]))

        elif data["type"] == "json":
            res = make_response(jsonify(data["next"]))

        elif data["type"] == "text":
            res = make_response(data["next"])

    else:
        res = make_response("Cookie unset successfully!")

    # unset cookie
    res.set_cookie(name, "", expires=0)

    # Return response
    return res


##
# @desc Check cookie for existence
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
# @desc Redirect not logged-in users
#
# @param url: str -- *Required url for users app
#
# @var next: str -- The next url
# 
# @return object
##
def login_required(app:str, controller:str=None, validate:str='user'):
    # Check app name
    if not app in apps:
        # Produce error message
        error = f'The "{app}" app doesn\'t exist!'

        # Check debug mode
        if debug:
            # Raise error
            raise Exception(error)

        else:
            # Print error
            print(error)
            exit()
    
    # Controller inserted
    if controller:
        # Controllers info
        module = importlib.import_module(f'controllers.{app}._controllers')
        controllers = getattr(module, 'controllers')

        # Check controller existence
        controller_exists = True
        while controller_exists:
            i = 0
            for ctrl in controllers:
                # Controller exists
                if controller in ctrl:
                    break
                
                i += 1

            controller_exists = False
            break

        if controller_exists:
            # Produce error message
            error = f'The "{app}" app doesn\'t have the "{controller}" controller!'

            # Check debug mode
            if debug:
                # Raise error
                raise Exception(error)

            else:
                # Print error
                print(error)
                exit()

        url = f'/{apps[app]}/{controllers[i][1]}/'

    # Controller not inserted
    else:
        url = f'/{apps[app]}/'

    def wrapper(inner):
        def decorator(*args, **kwargs):
            # Find next URL
            next = request.url.replace(request.url_root, '/')

            # User is not logged-in
            if not check_session(validate) and not check_cookie(validate):
                if next:
                    return redirect(f'{url}?next={next}')
                else:
                    return redirect(f'{url}?next={next}')

            # User is logged-in
            else:
                return inner(*args, **kwargs)

        return decorator
    return wrapper


##
# @desc Redirect logged-in users
#
# @param url: str -- *Required url for app
#
# @return object
##
def login_abort(app:str, controller:str=None, validate:str='user'):
    # Check app name
    if not app in apps:
        # Produce error message
        error = f'The "{app}" app doesn\'t exist!'

        # Check debug mode
        if debug:
            # Raise error
            raise Exception(error)

        else:
            # Print error
            print(error)
            exit()

    # Controller inserted
    if controller:
        # Controllers info
        module = importlib.import_module(f'controllers.{app}._controllers')
        controllers = getattr(module, 'controllers')

        # Check controller existence
        controller_exists = True
        while controller_exists:
            i = 0
            for ctrl in controllers:
                # Controller exists
                if controller in ctrl:
                    break
                
                i += 1

            controller_exists = False
            break

        if controller_exists:
            # Produce error message
            error = f'The "{app}" app doesn\'t have the "{controller}" controller!'

            # Check debug mode
            if debug:
                # Raise error
                raise Exception(error)

            else:
                # Print error
                print(error)
                exit()

        url = f'/{apps[app]}/{controllers[i][1]}/'

    # Controller not inserted
    else:
        url = f'/{apps[app]}/'

    def wrapper(inner):
        def decorator(*args, **kwargs):
            # return inner(*args, **kwargs)

            # User is logged-in
            if check_session(validate) or check_cookie(validate):
                return redirect(url)

            # User is not logged-in
            else:
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

