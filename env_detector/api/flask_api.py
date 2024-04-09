import time

import multiprocessing as mp
from multiprocessing.connection import Connection

from flask import Flask, request, jsonify
from flask_restx import Api, Resource

from env_detector.config import logger
from .routes import configure_routes


class FlaskAPI():
    
    def __init__(self, conn: Connection, host: str = '0.0.0.0', port: int = 5051):
        
        self._host = host
        self._port = port
        
        self._app_process = mp.Process(target=self._start_app, args=(conn, ))
        self._app_process.daemon = True
        
        
    def start(self):
        self._app_process.start()
        
    def _start_app(self, conn: Connection):
        app = Flask(__name__) 
        api = Api(app, version='1.0', title='Env-Detector API',
          description='Документация для сервсиа Env-Detector ')
        
        ns = api.namespace('api', description='Env-Detector  API')
        configure_routes(ns, conn) 
        app.run(host = self._host, port=self._port, debug=False, )
        # time.sleep(10)
        # queue.put({"cmd": "stop", "args": None}) 

