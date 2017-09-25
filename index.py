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
    optimum_change_speed = db.Column(db.REAL)
    simulation_status = db.Column(db.Text)

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
                "optimum_change_speed": float(request.form['optimum_change_speed'])
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
        
        
        # Transfer parameters from the form to the server through the scp 
        try:
            scp_parameters = subprocess.Popen("scp " + parameters_filename + " transp@wloczykij:/home/transp/simulations/webservice", 
                stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            stdout, stderr = scp_parameters.communicate()
        except Exception as e: 
            msg ="""There was a problem during submittion of your task.
                   This event was reported. 
                   Please, try again in a few minutes or contact us."""
            print(e)
            return render_template("task_submitted.html", task = msg)

        task = Task.query.get(task.id)
        task.simulation_status = "Pending"
        db.session.commit()
        db.session.refresh(task)

        # program will wait run the simulations on the server
        try: 
            run_computation = subprocess.Popen("./program.py " + str(task.id), stdout=subprocess.PIPE, shell=True)
            out, err = run_computation.communicate()
            print("program.py, out: " + str(out))
            print("program.py, err: " + str(err))
            print("program.py is running...(?)")
        except Exception as e:
            print(e)
            return render_template("task_submitted.html", task = "program execution failed.")
        #output, _ = p.communicate()
        
        #task = Task.query.get(task.id)
        #task.simulation_status = "Pending"
        #db.session.commit()
        return render_template("task_submitted.html", task = task)
        
    tasks = Task.query.all()
    
    return render_template("index.html", zmienna = tasks[(len(tasks)-5):])


@app.route('/results/<ID>')
def results(ID):
    results = Task.query.get(ID)
    return render_template("results.html", results = results, ID = ID)
    
