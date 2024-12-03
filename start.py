import os
import sys
import uvicorn
from dotenv import load_dotenv
import argparse
from subprocess import Popen

#######################################################################################################################
if not os.access("config/.gitkeep", os.W_OK):
    os.chmod("/code/config/", 0o0777)
if not os.access("files/database/db/.gitkeep", os.W_OK):
    os.chmod("/code/files/database/db/", 0o0777)

#######################################################################################################################
pathfile = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + os.sep)
dotenv_path = os.path.join(pathfile, ".env")
load_dotenv(dotenv_path)

#######################################################################################################################
APP_ENV = os.environ.get("EVIRONMENT", "DEVELOPMENT")
APP_URL = os.environ.get("APP_URL", "127.0.0.1")
APP_PORT = os.environ.get("APP_PORT", "8014")

if __name__ == "__main__":
    ###################################################################################################################
    print("### APP START ################################################################################################")
    print("APP_ENV  : ", APP_ENV)
    print("APP_URL  : ", APP_URL)
    print("APP_PORT : ", APP_PORT)
    if APP_ENV == "PRODUCTION":
        uvicorn.run(
            "app:app",
            port=int(APP_PORT),
            host=APP_URL,
            reload_dirs=["app"],
            workers=2,
            log_level="warning",
            reload=True,
        )
    else:
        uvicorn.run(
            "app.main:app",
            port=int(APP_PORT),
            host=APP_URL,
            reload=True,
            reload_dirs=["app"],
        )
