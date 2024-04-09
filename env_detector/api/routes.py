import pickle
import base64

from flask import Flask, request, jsonify
from flask_restx import Api, Namespace, Resource, fields
from multiprocessing.connection import Connection

from env_detector.config import logger
from env_detector.utils import Commands

def configure_routes(ns: Namespace, conn: Connection):
    
    message_response_model = ns.model('MessageResponse', {
    'message': fields.String,
    })

    fps = ns.model('FPS', {
        'fps': fields.Integer(required=True, description='fps'),
    })
    

    @ns.route('/Suspend')
    class SuspendService(Resource):
        def post(self):
            logger.info("POST Suspend")
            conn.send({"cmd": Commands.STOP, "args": None})
            return {"message": "Service suspended"}, 200

    @ns.route('/Continue')
    class ContinueService(Resource):
        def post(self):
            logger.info("POST Continue")
            conn.send({"cmd": Commands.START, "args": None})
            return {"message": "Service continued"}, 200

    @ns.route('/SetFPS')
    class SetFPS(Resource):
        @ns.expect(fps)
        def post(self):
            fps = request.json.get('fps')
            conn.send({"cmd": Commands.SET_FPS, "args": fps})
            return {"message": f"fps {fps} set"}, 200

    @ns.route('/GetFPS')
    class GetFPS(Resource):
        def get(self):
            conn.send({"cmd": Commands.GET_FPS, "args": None})
            msg = conn.recv()
            if msg["cmd"] == Commands.GET_FPS:
                fps = msg["args"]
                return {"roi": fps}, 200
            return {"message": "Get ROI functionality not implemented"}, 501
        
    @ns.route('/SetRefSSIM')
    class SetRefSSIM(Resource):
        def post(self):
            conn.send({"cmd": Commands.SET_REF_SSIM, "args": None})
            return {"message": f"set new reference frame ssim"}, 200


if __name__ == '__main__':
    app = Flask(__name__)
    configure_routes(app)
    app.run(host='0.0.0.0', port=5050, debug=True)