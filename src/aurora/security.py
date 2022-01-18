################
# Dependencies #
################
from os import replace
from flask import session, request, redirect
from werkzeug.security import check_password_hash, generate_password_hash


##
# @desc Redirect not logged-in users
#
# @param url: str -- *Required url for users app
#
# @var next: str -- The next url
#
# @return object
##
def login_required(url:str):
    def wrapper(inner):
        def decorator(*args, **kwargs):
            # Find next URL
            next = request.url.replace(request.url_root, '/')

            # User is not logged-in
            if not 'user' in session and not 'user' in request.cookies:
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
def login_abort(url:str):
    def wrapper(inner):
        def decorator(*args, **kwargs):
            # return inner(*args, **kwargs)

            # User is logged-in
            if 'user' in session or 'user' in request.cookies:
                return redirect(url)

            # User is not logged-in
            else:
                return inner(*args, **kwargs)

        return decorator
    return wrapper

