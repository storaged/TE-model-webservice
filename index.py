import subprocess
import pickle
import additional_info as info
from flask import Flask, render_template, request, send_file
#from flask_sqlalchemy import SQLAlchemy
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

from models import db, SimStat

db.init_app(app)
migrate = Migrate(app, db)

def get_parameters_dict(my_form):
    params = {}
    print(str(my_form))
    return {}

HOST = "transp@wloczykij"
WEBSERVICE_DIR = "/home/transp/simulations/webservice"
WEBSERVICE_PATH = HOST + ":" + WEBSERVICE_DIR 

#########
# VIEWS #
#########
@app.route('/', methods = ['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        parameters = request.form.to_dict()
        valid, tasks, errors = info.split_parameters(parameters)
        if not valid:
            return render_main_page(errors)
        else:
            job_id = 0
            for batch_id, batch in enumerate(tasks):
                task = info.Task(**batch)
                db.session.add(task)
                db.session.commit()
                db.session.refresh(task)

                if job_id == 0:
                    task_max_job_id = db.session.query(db.func.max(info.Task.job_id)).scalar() 
                    job_id = int(task_max_job_id) + 1 #task.id

                    parameters_filename = "parameters_" + str(job_id) + ".dat"
                    with open(parameters_filename, 'wb') as handler:
                        pickle.dump(parameters, handler, protocol = 2)
                    
                
                    # Transfer parameters from the form to the server through the scp 
                    try:
                        scp_parameters = subprocess.Popen(
                                "scp " + parameters_filename + " " + WEBSERVICE_PATH, 
                                stdout = subprocess.PIPE, stderr = subprocess.PIPE, 
                                shell = True)
                        stdout, stderr = scp_parameters.communicate()
                    except Exception as e: 
                        msg ="""There was a problem during the submittion of your task.
                               This event was reported. 
                               Please, try again in a few minutes or contact us."""
                        return render_template("task_submitted.html", task = msg)

                task = info.Task.query.get(task.id)
                task.simulation_status = SimStat.Queued
                task.job_id = job_id
                task.batch_id = batch_id
                db.session.commit()
                db.session.refresh(task)

                # program will wait run the simulations on the server
                if batch_id == len(tasks) - 1:
                    try: 
                        run_computation = subprocess.Popen(
                                "./program.py " + str(job_id), 
                                stdout=subprocess.PIPE, shell=True)
                    except Exception as e:
                        return render_template("task_submitted.html", task = "program execution failed.")
                    
            return render_template("task_submitted.html", task = task)
                
    return render_main_page({})

def render_main_page(errors):
    ## NON-POST ACITON
    ## Prepare some variables for the template
    ## Create a list of existing tasks
    tasks = info.Task.query.all()

    ## Updating completed tasks
    for task in tasks:
        task = info.Task.query.get(task.id)
        if task.simulation_status == SimStat.Queued:
            exists = subprocess.Popen("ssh transp@wloczykij test -d " + WEBSERVICE_DIR
                    + "/model-transposons-" + str(task.job_id) 
                    + " && printf OK",
                    stdout=subprocess.PIPE, shell=True)
            out, _ = exists.communicate()
            if out.decode() == "OK":
                task.simulation_status = SimStat.Pending
                db.session.commit()
                db.session.refresh(task)
        if task.simulation_status == SimStat.Pending:
            exists = subprocess.Popen("ssh transp@wloczykij test -f " + WEBSERVICE_DIR
                    + "/model-transposons-" + str(task.job_id) 
                    + "/batch-run-" + str(task.batch_id) + "/plot-3.png && printf OK",
                    stdout=subprocess.PIPE, shell=True)
            out, _ = exists.communicate()
            if out.decode() == "OK":
                task.simulation_status = SimStat.Complete
                db.session.commit()
                db.session.refresh(task)

    ## Prepare for the display of the results
    tasks_list, names = info.tasks_to_list(tasks[(len(tasks) - 10):len(tasks)],
            info.get_parameters_order())    
    
    ## Get all parameters for the task form
    cols_num = 3 #math.floor(math.sqrt(len(tmp))) + 1
    general_params, te_params = info.get_Task_parameters(cols_num,
            info.get_parameters_description(), info.get_parameters_defaults())

    return render_template("index.html", zmienna = tasks[(len(tasks)-10):],
            tasks_list = tasks_list, names = names, 
            params_general = general_params, params_TE = te_params,
            errors=errors)


@app.route('/results/<JOB_ID>/<BATCH_ID>')
def results(JOB_ID, BATCH_ID):
    results = info.Task.query.filter_by(job_id = JOB_ID, batch_id =
            BATCH_ID).first()
    images_list = info.get_images_list(results.TE_starting_te_no,
            results.TE_inactivation_probability, results.TE_deauton_probability)

    return render_template("results.html", results = results, id = JOB_ID, 
            batch = BATCH_ID, images_list = images_list)
   
@app.route('/results/images/<ID>/<BATCH>/<IMG_NAME>')
def getImage(ID, BATCH, IMG_NAME):
    import sys
    import pycurl 
    import io 

    HOST        = 'wloczykij'
    USER        = 'sftp://transp'
    WEBSERV_DIR = '/home/transp/simulations/webservice/'
    PATH_TO_KEY = '/home/krzysiek/.ssh/id_rsa'
    
    #IMG_NAME    = "plot-3.png"
     
    url   = USER + "@" + HOST + ":" + WEBSERV_DIR + 'model-transposons-' + ID + "/batch-run-" + BATCH + "/" + IMG_NAME
    
    print(url)

    storage = io.BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    storage.seek(0)

    #response = io.BytesIO(storage.getValue())

    #storage.close()

    #c.close()
    return send_file(io.BytesIO(storage.getvalue()),
                     attachment_filename=IMG_NAME,
                     mimetype='image/png')
    

if __name__ == "__main__":
    app.run()
