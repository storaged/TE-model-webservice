import subprocess
import pickle
import additional_info as info
from flask import Flask, render_template, request, send_file
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
    simulation_status = db.Column(db.Text)

    ############################
    # environmental parameters #
    ############################
    niche_size              = db.Column(db.Integer, default = 5000)
    optimum_change_speed    = db.Column(db.REAL, default = 0.01)
    selection_radius        = db.Column(db.REAL, default = 20.0)    # default: 20.0
    number_of_generations   = db.Column(db.Integer, default = 2000)

    # expected_horiz_transfers      = 0.0 | CONST
    # random_pressure               = 0.0 | CONST
    # min_survival_fitness          = 0.0 | CONST
    # stability_period              = 0   | CONST

    #########################
    # individual parameters #
    #########################
    number_of_traits        = db.Column(db.Integer) # no_phenotype_properties
    random_mutation_rate    = db.Column(db.REAL)    # default: 0.003
    
    # non_transposition_mutation_stdev    = 1.0 | CONST
    # genome_size               = 1     | CONST
    # tree_mode                 = True  | CONST
    # initial_phenotype_stdev   = 0.01  | CONST
    # sexual_mode               = True  | CONST
   
    #########################
    # TE related parameters #
    #########################
    TE_starting_te_no           = db.Column(db.Integer)
    TE_deauton_probability      = db.Column(db.REAL) # default: 0.0
    TE_inactivation_probability = db.Column(db.REAL) # default: 0.003
    TE_transposition_rate       = db.Column(db.REAL) # default: 0.003
    TE_deletion_probability     = db.Column(db.REAL) # default: 0.003
    
    # transposition_mutation_stdev          = 1.0   | CONST 'YARD STICK'
    # transposition_dynamics                = arnaud| CONST
    # transposon_creation_rate              = 0.0   | CONST
    # nonlethal_transposition_likelihood    = 1.0   | CONST
    # duplicative_transposition_probability = 1.0   | CONST
    # te_mutation_change_binding            = True  | CONST
    # autonomous_transp_dynamics            = arnaud| CONST
    
    #number_of_mutations   = 0
    #expected_mutation_shift   = 0.0
    #is_drift_directed   = True
    #fluctuations_magnitude   = 0.0

    # reproducer   = location_mode_off
    # killer   = null
    # pint   = 3
    # run_no   = 0
    # big_data_collection_every   = 500
    # plots_enabled   = True
    # tmpdir   = /home/transp/tmp
    # location_mode   = False
    # self_breeding   = False
    # offspring_size   = 5
    # multidim_changes   = True
    # uniform_offspring   = False
    
    

def tasks_to_list(tasks, ordering):
    mylist = []
    names = []
    first = True
    for task in tasks:
        values = []
        task_dir = dir(task)
        for param in ordering:
            if param in task_dir:
                if first: names.append(param)
                values.append(getattr(task, param))
        first = False
        mylist.append(values)
    return mylist, names

def get_Task_parameters(ncols, parameters_desc, defaults):
    te_params = []
    general_params = []
    for attr in dir(Task):
        if not attr.startswith("_") and attr not in ["metadata", "query",
                "query_class", "id", "simulation_status"]:
            if attr.startswith("TE_"):
                param = info.Parameter(attr, attr, parameters_desc[attr],
                        defaults[attr])
                te_params.append(param)
            else:
                param = info.Parameter(attr, attr, parameters_desc[attr],
                        defaults[attr])
                general_params.append(param)
    general_params = [general_params[i:i+ncols] for i in range(0,
        len(general_params), ncols)]
    te_params = [te_params[i:i+ncols] for i in range(0,
        len(te_params), ncols)]

    return general_params, te_params

def get_parameters_dict(my_form):
    params = {}
    print(str(my_form))
    return {}

#########
# VIEWS #
#########
@app.route('/', methods = ['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        
        parameters = request.form.to_dict()
        
        task = Task(**parameters)
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
            #out, err = run_computation.communicate()
            #print("program.py, out: " + str(out))
            #print("program.py, err: " + str(err))
            #print("program.py is running...(?)")
        except Exception as e:
            print(e)
            return render_template("task_submitted.html", task = "program execution failed.")
        #output, _ = p.communicate()
        
        return render_template("task_submitted.html", task = task)
        
    ## NON-POST ACITON
    ## Prepare some variables for the template
    ## Create a list of existing tasks
    tasks = Task.query.all()
    tasks_list, names = tasks_to_list(tasks[(len(tasks) - 5):len(tasks)],
            info.get_parameters_order())    
    
    ## Get all parameters for the task form
    cols_num = 3 #math.floor(math.sqrt(len(tmp))) + 1
    general_params, te_params = get_Task_parameters(cols_num,
            info.get_parameters_description(), info.get_parameters_defaults())

    return render_template("index.html", zmienna = tasks[(len(tasks)-5):],
            tasks_list = tasks_list, names = names, 
            params_general = general_params, params_TE = te_params)


@app.route('/results/<ID>')
def results(ID):
    results = Task.query.get(ID)

    return render_template("results.html", results = results, ID = ID)
   
@app.route('/results/images/<ID>/<BATCH>')
def getImage(ID, BATCH):
    import sys
    import pycurl 
    import io 

    HOST        = 'wloczykij'
    USER        = 'sftp://transp'
    WEBSERV_DIR = '/home/transp/simulations/webservice/'
    PATH_TO_KEY = '/home/krzysiek/.ssh/id_rsa'
    
    IMG_NAME    = "plot-3.png"
     
    url   = USER + "@" + HOST + ":" + WEBSERV_DIR + 'model-transposons-' + ID + "/batch-run-" + BATCH + "/" + IMG_NAME
    
    print(url)

    storage = io.StringIO()

    c = pycurl.Curl()
    #c.setopt(c.URL, url)
    #c.setopt(c.WRITEFUNCTION, storage.write)
    #c.perform()
    #storage.seek(0)

    #response = io.BytesIO(storage.getValue())

    #storage.close()

    #c.close()
    return send_file(storage,
                     attachment_filename=IMG_NAME,
                     mimetype='image/png')

if __name__ == "__main__":
    app.run()
