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
    simulation_status = db.Column(db.Text)

    ############################
    # environmental parameters #
    ############################
    niche_size              = db.Column(db.Integer)
    optimum_change_speed    = db.Column(db.REAL)
    selection_radius        = db.Column(db.REAL)    # default: 20.0
    number_of_generations   = db.Column(db.Integer)

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
    
    

def tasks_to_list(tasks):
    mylist = []
    names = []
    first = True
    for task in tasks:
        mydir = {}
        for attr in dir(task):
            if not attr.startswith("_") and attr not in ["metadata", "query", "query_class"]:
                if first:
                    names.append(attr)
                mydir[attr] = getattr(task, attr)
        first = False
        mylist.append(mydir)
    return mylist, names

def get_Task_parameters(ncols):
    te_params = []
    general_params = []
    for attr in dir(Task):
        if not attr.startswith("_") and attr not in ["metadata", "query",
                "query_class", "id", "simulation_status"]:
            if attr.startswith("TE_"):
                te_params.append(attr.replace("TE_", ""))
            else:
                general_params.append(attr)
    general_params = [general_params[i:i+ncols] for i in range(0,
        len(general_params), ncols)]
    general_params = [general_params[i:i+ncols] for i in range(0,
        len(general_params), ncols)]

    return general_params, te_params


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
        
        return render_template("task_submitted.html", task = task)
        
    ## Prepare some variables for the template 
    tasks = Task.query.all()
    tasks_list, names = tasks_to_list(tasks)    
    
    cols_num = 3 #math.floor(math.sqrt(len(tmp))) + 1
    general_params, te_params = get_Task_parameters(cols_num)


    # tmp = list(filter(lambda x: x not in ['id', 'simulation_status'], names))
    # general_params = [general_params[i:i+cols_num] for i in range(0,
    #    len(general_params), 3)]

    return render_template("index.html", zmienna = tasks[(len(tasks)-5):],
            tasks_list = tasks_list, names = names, params_general = general_params, params_TE = te_params)


@app.route('/results/<ID>')
def results(ID):
    results = Task.query.get(ID)
    return render_template("results.html", results = results, ID = ID)
   
if __name__ == "__main__":
    app.run()
