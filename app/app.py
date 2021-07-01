from flask import Flask, jsonify
from random import randint
from flask_restful import reqparse, Api, Resource
from werkzeug.exceptions import HTTPException
import json
import os

onecak = Flask(__name__)
api = Api(onecak)
port = int(os.environ.get("PORT", 5000))
database = json.load(open('./database/onecak.json'))
length = database['length']
lastPost = database['lastpost']
lastScan = database['lastscan']
posts = database['posts']

class Home(Resource):
    def get(self):
        return jsonify({
            "name": "onecak",
            "credit": "https://1cak.com",
            "license": "MIT",
            "sourcecode": "https://github.com/dickymuliafiqri/onecak"
        })

class OneCakShuffle(Resource):
    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument('entity')
        self.args = parser.parse_args()

    def get(self):
        result = []
        entity = self.args['entity'] if self.args['entity'] else 1
        if type(entity) != type(1): entity = int(entity.replace('/', ''))
        if entity > 10:
            return jsonify({
                "message": "max entity is 10"
            })
        for i in range(entity):
            result.append(posts[randint(0, length-1)])
        return jsonify({
            "length": len(result),
            "posts": result,
            "lastpost": lastPost
        })

class OneCakLol(Resource):
    def get(self):
        result = []
        for indx in range(length-1, length-11, -1):
            result.append(posts[indx])
        return jsonify({
            "length": len(result),
            "posts": result,
            "lastpost": lastPost
        })

api.add_resource(Home, '/')
api.add_resource(OneCakShuffle, '/shuffle/')
api.add_resource(OneCakLol, '/lol/')

@onecak.errorhandler(HTTPException)
def exception_handler(e):
    res = e.get_response()
    res.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description
    })
    res.content_type = "application/json"
    return res

if __name__ == '__main__':
    onecak.run(debug=False, host="0.0.0.0", port=port)