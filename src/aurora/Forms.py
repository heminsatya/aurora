################
# Dependencies #
################
import importlib
from wtforms import *
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta
from flask import session

config = importlib.import_module('config')
secret_key = getattr(config, "SECRET_KEY")


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
        csrf_secret = bytes('{}'.format(secret_key), encoding='utf8')
        csrf_time_limit = timedelta(minutes=20)
        csrf_context = session
