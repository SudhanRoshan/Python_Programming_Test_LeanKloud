from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_mysqldb import MySQL
from configFile import dbConfigs
from datetime import date
import time


app = Flask(__name__)

# MySQL database configurations

app.config["MYSQL_HOST"] = dbConfigs["hostName"]
app.config["MYSQL_USER"] = dbConfigs["userName"]
app.config["MYSQL_PASSWORD"] = dbConfigs["password"]
app.config["MYSQL_DB"] = dbConfigs["dbName"]

# Initializing DB for the App
mysql = MySQL(app)


app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
          description='A simple TodoMVC API',)


ns = api.namespace('todos', description='TODO operations')


todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='Task details'),
    # Adding two new fields to each task (due_date and status)
    'due_date': fields.String(required=True, description='Task due date'),
    'status': fields.String(required=True, description='Status of the task'),
})


# Main Class

class TodoDAO(object):

    # Initializing id counter and todos list
    def __init__(self):
        self.counter = 0
        self.todos = []

# Helper function for POST and PUT methods
    def createOrUpdateTask(self, data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        self.todos.append(todo)
        return todo


# Helper functions for all the GET methods


    def showAllTasks(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        sourceTuples = cur.fetchall()
        # sourceTuples contains all tasks that are stored in the MySQL DB as Tuple datatype
        tasksRequired = []
        # tasksRequired refers to the tasks that are satisfied the condition of GET method
        for task in sourceTuples:
            tasksRequired.append({"id": task[0], "task": task[1],
                                  "due_date": task[2], "status": task[3]})
        return tasksRequired

    def showFinishedTasks(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        sourceTuples = cur.fetchall()
        tasksRequired = []
        for task in sourceTuples:
            if task[3] == "Finished":
                tasksRequired.append({"id": task[0], "task": task[1],
                                      "due_date": task[2], "status": task[3]})
        return tasksRequired

    def showOverdueTasks(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        sourceTuples = cur.fetchall()
        tasksRequired = []
        for task in sourceTuples:
            dueDate = task[2]
            formattedDueDate = time.strptime(dueDate, "%Y-%m-%d")
            currentDate = date.today()
            strCurrentDate = str(currentDate)
            formattedCurrentDate = time.strptime(strCurrentDate, "%Y-%m-%d")
            if formattedDueDate < formattedCurrentDate and task[3] != "Finished":
                tasksRequired.append({"id": task[0], "task": task[1],
                                      "due_date": task[2], "status": task[3]})
        return tasksRequired

    def showATask(self, id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        sourceTuples = cur.fetchall()
        tasksRequired = []
        for task in sourceTuples:
            if task[0] == id:
                tasksRequired.append({"id": task[0], "task": task[1],
                                      "due_date": task[2], "status": task[3]})
        return tasksRequired

    def showDueTasks(self, due_date):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos")
        sourceTuples = cur.fetchall()
        tasksRequired = []
        for task in sourceTuples:
            if task[2] == due_date and task[3] != "Finished":
                tasksRequired.append({"id": task[0], "task": task[1],
                                      "due_date": task[2], "status": task[3]})
        return tasksRequired


# Object declaration
DAO = TodoDAO()


# Route for getting all tasks and for creating a new task

@ns.route("/")
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        allTasks = DAO.showAllTasks()
        return allTasks

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        sourceDictionary = DAO.createOrUpdateTask(api.payload)
        # sourceDictionary contains all inputs provided by user such as task,due_date and status as Dictionary datatype
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO todos(task,due_date,status,id) VALUES(%s,%s,%s,%s)", (
            sourceDictionary["task"], sourceDictionary["due_date"], sourceDictionary["status"], sourceDictionary["id"]))
        mysql.connection.commit()
        cur.close()
        return sourceDictionary, 201


# Additional endpoint (i.e) "GET/finished"
# Route for getting finished tasks

@ns.route("/finished")
class getFinished(Resource):
    '''Shows a list of all todos that are finished'''
    @ns.doc('list_finished_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all the finished tasks'''
        finishedTasks = DAO.showFinishedTasks()
        return finishedTasks


# Additional endpoint (i.e) "GET/overdue"
# Route for getting overdue tasks

@ns.route("/overdue")
class getOverdue(Resource):
    '''Shows a list of all todos that are overdue'''
    @ns.doc('list_overdue_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all the overdue tasks'''
        overdueTasks = DAO.showOverdueTasks()
        return overdueTasks


# Route for getting,deleting and updating a task given its id

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete and edit them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a task given its id'''
        aTask = DAO.showATask(id)
        return aTask

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM todos WHERE id = {}".format(id))
        mysql.connection.commit()
        return "DELETED"

# We can change the status of task using below method if given an identifier
# Route for updating the task details given its id

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        sourceDictionary = DAO.createOrUpdateTask(api.payload)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE todos SET task = %s, due_date = %s,status=%s WHERE id ={}".format(
            id), (sourceDictionary["task"], sourceDictionary["due_date"], sourceDictionary["status"]))
        mysql.connection.commit()
        return "UPDATED"


# Additional endpoint (i.e) "GET/due?due_date=yyyy-mm-dd"
# Route for getting tasks due given the date

@ns.route('/<string:due_date>')
@ns.response(404, 'No Dues')
@ns.param('due_date', 'Due date for the task')
class getTodosForGivenDate(Resource):
    '''Shows due with given date'''
    @ns.doc('get_dues_with_given_date')
    @ns.marshal_with(todo)
    def get(self, due_date):
        '''Fetch dues of the day'''
        dueTasks = DAO.showDueTasks(due_date)
        return dueTasks


if __name__ == '__main__':
    app.run(debug=True)
