from flask import Flask, jsonify
from random import randint
from flask_restful import reqparse, Api, Resource
from werkzeug.exceptions import HTTPException
import json
import os
import crud

onecak = Flask(__name__)
api = Api(onecak)
port = int(os.environ.get("PORT", 5000))

class OnecakAPI(Resource):
    def __init__(self):
        self.database = crud.OnecakDB()
        self.length = self.database.run_command('''SELECT database_length FROM tasks''')
        self.lastPost = self.database.run_command('''SELECT recent_post FROM tasks''')
        self.lastScan = self.database.run_command('''SELECT last_scan FROM tasks''')
        parser = reqparse.RequestParser()
        parser.add_argument('lol')
        parser.add_argument('shuffle')
        self.args = parser.parse_args()

    def get(self):
        result = []
        lol = None if self.args['lol'] == None else 1
        shuffle = 1 if self.args['shuffle'] == '' else self.args['shuffle']
        shuffle = int(shuffle) if type(shuffle) == type('str') else shuffle

        if lol:
            for indx in range(self.length, self.length-10, -1):
                data = self.database.run_command('SELECT json_value FROM posts WHERE id = {}'.format(indx))
                result.append(data)
            return jsonify({
                "length": len(result),
                "posts": result,
                "lastpost": self.lastPost
            })
        
        elif shuffle:
            if shuffle > 10:
                return jsonify({
                    "message": "max entity is 10"
                })
            loop = 0
            while True:
                data = self.database.run_command('SELECT json_value FROM posts WHERE id = {}'.format(randint(1, self.length)))
                result.append(data)
                loop += 1
                if loop >= shuffle: break
            return jsonify({
                "length": len(result),
                "posts": result,
                "lastpost": self.lastPost
            })

        return jsonify({
            "name": "onecak",
            "credit": "https://1cak.com",
            "license": "MIT",
            "sourcecode": "https://github.com/dickymuliafiqri/onecak"
        })

api.add_resource(OnecakAPI, '/')

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