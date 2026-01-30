import ee
import os
import json
import traceback
from google.oauth2 import service_account

def initialize_gee():
    """
    Initializes Google Earth Engine using the Service Account credentials
    specified in GOOGLE_APPLICATION_CREDENTIALS.
    """
    key_path = None
    try:
        # Proceed with initialization
        key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not key_path:
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set in environment.")

        if not os.path.exists(key_path):
            raise Exception(f"GEE Key file not found at: {key_path}")

        # Authenticate with Service Account using google-auth
        # Standard way for modern earthengine-api
        credentials = service_account.Credentials.from_service_account_file(key_path)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/earthengine'])
        
        ee.Initialize(credentials=scoped_credentials)
        print("Google Earth Engine initialized successfully.")
        return True

    except Exception as e:
        error_msg = f"FAILED to initialize Google Earth Engine.\nKey Path: {key_path}\nError: {e}\n{traceback.format_exc()}"
        print(error_msg)
        
        # Log to file to bypass truncation
        try:
            with open("gee_error.log", "w") as f:
                f.write(error_msg)
        except:
            pass
            
        return False
