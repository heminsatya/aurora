################
# Dependencies #
################
from flask import request
from flask.views import View


####################
# Controller Class #
####################
##
# @desc Controller class to control views based on the requested method 
##
class Controller(View):

    ##
    # @desc Flask dispatch_request method -- Generates Pluggable Views
    ##
    def dispatch_request(self, *class_args, **class_kwargs):
        # Check the requested methods then return the related view function
        # The 'POST' request
        if request.method == 'POST':
            return self.post(*class_args, **class_kwargs)

        # The 'GET' request
        elif request.method == 'GET':
            return self.get(*class_args, **class_kwargs)

        # The 'PUT' request
        elif request.method == 'PUT':
            return self.put(*class_args, **class_kwargs)

        # The 'DELETE' request
        elif request.method == 'DELETE':
            return self.delete(*class_args, **class_kwargs)


    ##
    # @desc get method placeholder -- To handle the 'GET' requests
    # 
    # @return any
    ##
    def post(self):
        return 'POST Method'


    ##
    # @desc get method placeholder -- To handle the 'GET' requests
    # 
    # @return any
    ##
    def get(self):
        return 'GET Method'
     

    ##
    # @desc get method placeholder -- To handle the 'GET' requests
    # 
    # @return any
    ##
    def put(self):
        return 'PUT Method'
     

    ##
    # @desc get method placeholder -- To handle the 'DELETE' requests
    # 
    # @return any
    ##
    def delete(self):
        return 'DELETE Method'

