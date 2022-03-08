from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import date
import time
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Roshan02"
app.config["MYSQL_DB"] = "flaskapp"
mysql = MySQL(app)


app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
          description='A simple TodoMVC API',
          )

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),

    # Adding two new fields to each task (due_date and status)

    'due_date': fields.String(required=True, description='The task due'),
    'status': fields.String(required=True, description='The status of the task'),
})


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def getTodos(self, due_date):
        result = []
        for todo in self.todos:
            if todo["due_date"] == due_date and todo["status"] != "Finished":
                result.append(todo)
        return result

    def create(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        self.todos.append(todo)
        return todo

    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        return todo

    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)


DAO = TodoDAO()


@ns.route("/")
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        x = cur.fetchall()
        result = []
        for i in x:
            result.append({"id": i[0], "task": i[1],
                          "due_date": i[2], "status": i[3]})
        return result

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO todos(task,due_date,status,id) VALUES(%s,%s,%s,%s)", (DAO.create(
            api.payload)["task"], DAO.create(api.payload)["due_date"], DAO.create(api.payload)["status"], DAO.create(api.payload)["id"]))
        mysql.connection.commit()
        cur.close()
        return DAO.create(api.payload), 201

# Additional endpoint (i.e) "GET/finished"


@ns.route("/finished")
class getFinished(Resource):
    '''Shows a list of all todos that are finished'''
    @ns.doc('list_finished_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all the finished tasks'''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        y = cur.fetchall()
        result = []
        for i in y:
            if i[3] == "Finished":
                result.append({"id": i[0], "task": i[1],
                               "due_date": i[2], "status": i[3]})
        return result


# Additional endpoint (i.e) "GET/overdue"

@ns.route("/overdue")
class getOverdue(Resource):
    '''Shows a list of all todos that are overdue'''
    @ns.doc('list_overdue_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all the overdue tasks'''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        z = cur.fetchall()
        result = []

        for i in z:
            dueDate = i[2]
            formattedDueDate = time.strptime(dueDate, "%Y-%m-%d")
            currentDate = date.today()
            strCurrentDate = str(currentDate)
            formattedCurrentDate = time.strptime(strCurrentDate, "%Y-%m-%d")
            if formattedDueDate < formattedCurrentDate and i[3] != "Finished":
                result.append({"id": i[0], "task": i[1],
                               "due_date": i[2], "status": i[3]})
        return result


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        a = cur.fetchall()
        result = []
        for i in a:
            if i[0] == id:
                result.append({"id": i[0], "task": i[1],
                               "due_date": i[2], "status": i[3]})
        return result

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM todos WHERE id = {}".format(id))
        mysql.connection.commit()
        return "DELETED"

# We can change the status of task using below method if given an identifier

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        cur = mysql.connection.cursor()

        cur.execute("UPDATE todos SET task = %s, due_date = %s,status=%s WHERE id ={}".format(id),
                    (DAO.create(
                        api.payload)["task"], DAO.create(api.payload)["due_date"], DAO.create(api.payload)["status"], ))
        mysql.connection.commit()
        return "UPDATED"
        return DAO.update(id, api.payload)

# Additional endpoint (i.e) "GET/due?due_date=yyyy-mm-dd"


@ns.route('/<string:due_date>')
@ns.response(404, 'No Dues')
@ns.param('due_date', 'Due date for the task')
class getTodosForGivenDate(Resource):
    '''Shows dues with given date'''
    @ns.doc('get_dues_with_given_date')
    @ns.marshal_with(todo)
    def get(self, due_date):
        '''Fetch dues of the day'''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        b = cur.fetchall()
        result = []
        for i in b:
            if i[2] == due_date and i[3] != "Finished":
                result.append({"id": i[0], "task": i[1],
                               "due_date": i[2], "status": i[3]})
        return result


if __name__ == '__main__':
    app.run(debug=True)
