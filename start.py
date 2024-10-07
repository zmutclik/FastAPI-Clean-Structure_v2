import os
import uvicorn
from dotenv import load_dotenv
import argparse
from subprocess import Popen
#######################################################################################################################
parser = argparse.ArgumentParser(description="Start Applikasi.", epilog="Pilih Module yang mau diJalankan.")
parser.add_argument("module", help="Pilih salah satu = ws, celery atau fower")
args = parser.parse_args()

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
    print("APP_ENV : ", APP_ENV)
    if args.module == "ws":
        if APP_ENV == "PRODUCTION":
            uvicorn.run(
                "app.main:app",
                port=int(APP_PORT),
                host=APP_URL,
                reload_dirs=["app"],
                workers=2,
                # reload=True,
                # log_level="warning",
                # no_access_log=True,
                # ssl_keyfile='config/ssl/privkey.pem',
                # ssl_certfile='config/ssl/cert.pem'
            )
        else:
            uvicorn.run(
                "app.main:app",
                port=int(APP_PORT),
                host=APP_URL,
                reload=True,
                reload_dirs=["app"],
            )
    
    
    # if args.module == "celery":
        # exec( "python -m celery -A worker.celery.celery_app worker --loglevel=info"  )
