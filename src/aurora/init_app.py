################
# Dependencies #
################
import os
import time
import platform
import importlib
from .helpers import dir_empty, copy_file, delete_file, unzip_file


###########################
# Initialize the root app #
###########################
def start():
    # Check platform system
    # Windows
    if platform.system() == 'Windows':
        url_div = '\\'

    # Linux, Mac
    else:
        url_div = '/'

    # AuroraMVC path
    aurora_path = os.path.dirname(__file__)

    # App path (the caller)
    app_path = os.getcwd()

    # Check app directory
    if not dir_empty(app_path):
        print('The project direcory is not empty!')
        exit()

    # So far so good
    print('Initializing the root app...')
    time.sleep(0.5)

    # try the process
    try:
        init_bluprint = f'{aurora_path + url_div}blueprints{url_div}init_app.zip'
        init_file = f'{app_path + url_div}init_app.zip'

        # Copy the initial blueprint zip file
        copy_file(init_bluprint, init_file)

        # Unzip the file
        unzip_file(init_file, app_path)

        # Remove the zip file
        delete_file(init_file)

        # Check the safe type
        config = importlib.import_module('config')
        safe_type = getattr(config, 'SAFE_TYPE')

        if safe_type:
            users_model_bluprint = f'{aurora_path + url_div}blueprints{url_div}users_model_safe.zip'
        else:
            users_model_bluprint = f'{aurora_path + url_div}blueprints{url_div}users_model.zip'

        users_model_file = f'{app_path + url_div}models{url_div}users_model.zip'

        # Copy the Users model zip file
        copy_file(users_model_bluprint, users_model_file)

        # Unzip the file
        unzip_file(users_model_file, f'{app_path + url_div}models')

        # Remove the zip file
        delete_file(users_model_file)

        # Success
        print('The root app initialized successfully!')
        time.sleep(0.5)

        # Produce final the message
        message = 'To run the application use the following command:\n'
        message += 'python app.py'

        # Print the message
        print(message)

    # Handle the Error
    except NameError as err:
        # Print the error
        print(err)

    # Exit the Program
    finally:
        exit()


# Run the program
if __name__ == '__main__':
    start()
