import subprocess
import pickle
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

#################
# CONFIGURATION #
#################
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///TEmodelDB.sqlite3'
    )

###########################
# DATABASE INITIALIZATION #
###########################
db = SQLAlchemy()
db.init_app(app)

migrate = Migrate(app, db)

##########
# MODELS #
##########
class Task(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    niche_size = db.Column(db.Integer)
    number_of_traits = db.Column(db.Integer)
    optimum_change_speed = db.Column(db.Integer)
    simulation_status = db.Column(db.Integer)

#########
# VIEWS #
#########
@app.route('/', methods = ['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        
        for i in request.form.keys(): print(i)
        # dictionary of parameters submitted by user
        parameters = {
                "niche_size": int(request.form['niche_size']),
                "number_of_traits": int(request.form['number_of_traits']),
                "optimum_change_speed": int(request.form['optimum_change_speed'])
                }
        
        # create task entry
        task = Task(niche_size = parameters['niche_size'],
                    number_of_traits = parameters['number_of_traits'],
                    optimum_change_speed = parameters['optimum_change_speed'])

        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)

        parameters_filename = "parameters_" + str(task.id) + ".dat"
        with open(parameters_filename, 'wb') as handler:
            pickle.dump(parameters, handler, protocol = 2)
        
        
        # parameters are copied to the server
        scp_parameters = subprocess.Popen("scp " + parameters_filename + " transp@wloczykij:/home/transp/simulations/webservice", 
            stdout=subprocess.PIPE, shell=True)
        output, _ = scp_parameters.communicate()
        
        # program will wait run the simulations on the server
        run_computation = subprocess.Popen(['./program.py', 
            str(task.id)], stdout=subprocess.PIPE)
        
        #output, _ = p.communicate()
        task = Task.query.get(task.id)
        task.result = "Pending"
        db.session.commit()
        return render_template("task_submitted.html", task = task)
        
    tasks = Task.query.all()
    print(tasks)
    return render_template("index.html", zmienna = tasks)


@app.route('/results/<ID>')
def results(ID):
    results = Task.query.get(ID)
    return render_template("results.html", results = results, ID = ID)
    
