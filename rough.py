# PART I


from flask import Flask, request, jsonify
from flask_restx import Api, Resource, reqparse


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('due_date', type=str)

# http://127.0.0.1:5000/due?due_date="2022-03-05"


# parser = reqparse.RequestParser()
# parser.add_argument('rate', type=int, help='Rate to charge for this resource')
# args = parser.parse_args(strict=True)

todoDetails = [
    {"taskName": "LearningPython", "due_date_data": "2022-03-05", "status": "finished"},
    {"taskName": "Java", "due_date": "2022-03-05", "status": "inProgress"},
    {"taskName": "NodeJS", "due_date": "2022-03-05", "status": "started"},
    {"taskName": "Bathing", "due_date": "2022-03-05", "status": "notStarted"},
    {"taskName": "Cricket", "due_date": "2022-03-05", "status": "finished"},
    {"taskName": "Brushing", "due_date": "2022-03-05", "status": "finished"},
    {"taskName": "Eating", "due_date": "2022-03-05", "status": "finished"}
]


@api.route("/finished")
class getFinished(Resource):
    def get(self):
        result = []
        for i in todoDetails:
            if i["status"] == "finished":
                result.append(i)
        return {"data": result}


class getDue(Resource):
    def post(self, due_date):
        request.get_json(force=True)
        args = parser.parse_args()
        un = str(args['due_date'])
        # age = args['personal_data']['age']
        return jsonify(u=un)


api.add_resource(getDue, '/due')
app.run(debug=True)
