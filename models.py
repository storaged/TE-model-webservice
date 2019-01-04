#from index import db
#from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SimStat:
    Queued, Pending, Complete, Failed = "Queued", "Pending",\
            "Complete", "Failed" 

##########
# MODELS #
##########
class Task(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    simulation_status = db.Column(db.Text)
    batch_id = db.Column(db.Integer)
    job_id = db.Column(db.Integer)

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
 
