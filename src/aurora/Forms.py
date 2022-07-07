################
# Dependencies #
################
import importlib
from wtforms import *
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
from flask import session
from .helpers import random_string

# Set the csrf secret key
csrf_secret_key = random_string(24)


###############
# Forms Class #
###############
##
# @desc Forms class to handle WTForms CSRF Token
##
class Forms(Form):

    ##
    # @desc Constructor method
    ##
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    ##
    # @desc WTForms Meta Class
    ##
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = bytes('{}'.format(csrf_secret_key), encoding='utf8')
        csrf_time_limit = timedelta(minutes=20)
        csrf_context = session
