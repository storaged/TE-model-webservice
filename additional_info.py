from models import Task

class Parameter:
    def __init__(self, name, dbname, description, default, value = 0):
        self.name = name
        self.dbname = dbname
        self.desc = description
        self.default = default
        self.value = value

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
                "query_class", "id", "simulation_status", "batch_id","job_id"]:
            if attr.startswith("TE_"):
                param = Parameter(attr, attr, parameters_desc[attr],
                        defaults[attr])
                te_params.append(param)
            else:
                param = Parameter(attr, attr, parameters_desc[attr],
                        defaults[attr])
                general_params.append(param)
    general_params = [general_params[i:i+ncols] for i in range(0,
        len(general_params), ncols)]
    te_params = [te_params[i:i+ncols] for i in range(0,
        len(te_params), ncols)]

    return general_params, te_params

def validate_param(key, val):
    float_params = ["selection_radius", "optimum_change_speed",
        "random_mutation_rate", "TE_deauton_probability",
        "TE_inactivation_probability", "TE_transposition_rate", 
        "TE_deletion_probability"]
    integer_params = ["niche_size", "number_of_generations", "number_of_traits",
        "TE_starting_te_no"]
    try: 
        if key in float_params: 
            return float(val)
    except ValueError:
        raise Exception(key, val, "non-negative float")
    try:
        if key in integer_params:
            return int(val)
    except ValueError:
        raise Exception(key, val, "positive integer")


def split_parameters(params_dict):
    from itertools import product
    params_sep = {}
    errors_dict = {}
    valid = True
    for key, value in params_dict.items():
        values_list = value.split(',')
        res = []
        for x in values_list:
            try:
                res.append(validate_param(key, x))
            except Exception as inst:
                valid = False
                k_err, v_err, exp_type = inst.args
                errors_dict[k_err] = "Found: " + v_err\
                    + "; expected type: " + exp_type + "."
        params_sep[key] = res

    if valid:
        list_of_tasks = [dict(zip(params_sep.keys(), prod)) for prod in
            product(*params_sep.values())]
        return (valid, list_of_tasks, {})
    else:
        print(errors_dict)
        return (valid, {}, errors_dict)


def get_parameters_description():
    desc = {}

    desc["simulation_status"] = ""

    ############################
    # environmental parameters #
    ############################
    desc["niche_size"]              = "The number of individuals in "\
        "a population. During each generation individuals will reproduce "\
        "to during the simulation runtime.\nShould be a natural number.\n"
    desc["number_of_generations"]   = "How many life cycle repeats should be "\
        "performed during the simulation.\nShould be a natural number.\n"
    desc["selection_radius"]        = "When calculating the fitness of "\
        "an individual the parameter describes the level of tolerance in the "\
        "sense of adaptation to environmental conditions.\nShould be a "\
        "positive real number.\n"

    desc["optimum_change_speed"]    = "The value describes how fast "\
        "the optimal phenotype should change in every generation.\n"\
        "Should be a real number.\n"


    # expected_horiz_transfers      = 0.0 | CONST
    # random_pressure               = 0.0 | CONST
    # min_survival_fitness          = 0.0 | CONST
    # stability_period              = 0   | CONST

    #########################
    # individual parameters #
    #########################
    desc["number_of_traits"]        = "Describes the complexity of organism. "\
        "In other words how many properties does the an individual have. "\
        "Should be a natural number.\n"
    desc["random_mutation_rate"]    = "Rate at which random mutations occur "\
        " in an individual.\nShould be a posiitve real number.\n"
    
    # non_transposition_mutation_stdev    = 1.0 | CONST
    # genome_size               = 1     | CONST
    # tree_mode                 = True  | CONST
    # initial_phenotype_stdev   = 0.01  | CONST
    # sexual_mode               = True  | CONST
   
    #########################
    # TE related parameters #
    #########################
    desc["TE_starting_te_no"]           = "TODO\n\n"
    desc["TE_deauton_probability"]      = "TODO\n\n"
    desc["TE_inactivation_probability"] = "TODO\n\n"
    desc["TE_transposition_rate"]       = "TODO\n\n"
    desc["TE_deletion_probability"]     = "TODO\n\n"

    return desc


def get_parameters_defaults():
    desc = {}

    desc["simulation_status"] = ""

    ############################
    # environmental parameters #
    ############################
    desc["niche_size"]              = "2000"
    desc["number_of_generations"]   = "2000"
    desc["selection_radius"]        = "10.0"
    desc["optimum_change_speed"]    = "0.001"


    # expected_horiz_transfers      = 0.0 | CONST
    # random_pressure               = 0.0 | CONST
    # min_survival_fitness          = 0.0 | CONST
    # stability_period              = 0   | CONST

    #########################
    # individual parameters #
    #########################
    desc["number_of_traits"]        = "2"
    desc["random_mutation_rate"]    = "0.001"
    
    # non_transposition_mutation_stdev    = 1.0 | CONST
    # genome_size               = 1     | CONST
    # tree_mode                 = True  | CONST
    # initial_phenotype_stdev   = 0.01  | CONST
    # sexual_mode               = True  | CONST
   
    #########################
    # TE related parameters #
    #########################
    desc["TE_starting_te_no"]           = "0"
    desc["TE_deauton_probability"]      = "0.0"
    desc["TE_inactivation_probability"] = "0.0"
    desc["TE_transposition_rate"]       = "0.0"
    desc["TE_deletion_probability"]     = "0.0"

    return desc

def get_parameters_order():
    params_order = ["id", "job_id", "batch_id",
        ## Environmental parameters        
        "niche_size", "number_of_generations",
        "selection_radius", "optimum_change_speed", "expected_horiz_transfers",
        "random_pressure", "min_survival_fitness", "stability_period", 
        ## individual parameters 
        "number_of_traits", "random_mutation_rate",
        "non_transposition_mutation_stdev", "genome_size", "tree_mode",
        "initial_phenotype_stdev   = 0.01", "sexual_mode",
        ## TE related parameters 
        "TE_starting_te_no", "TE_deauton_probability",
        "TE_inactivation_probability", "TE_transposition_rate",
        "TE_deletion_probability",
        "simulation_status"]
    return params_order

def get_image_caption(image):
    captions = {}    
    captions["plot-3.png"] = "The figure presents the distribution of the "\
            "population's fitness during the whole simulation. "\
            "On the x-axis are generations, on the y-axis are "\
            "possible fitness values. For a given generation (x) and a fitness "\
            "value (y) the color of that point encodes the number "\
            "of individuals with the fitness (y) in the generation (x). " 
    captions["plot-output-singlevalue-environmental_change.bin.Rdata.png"]="The "\
    "plot presents the environmental change in time. "\
    "On the Y-axis is the distance from the starting optimal phenotype "\
    "in the generation (x)."
    captions["plot-output-singlevalue-avg_mutations.bin.Rdata.png"] = "Average "\
            "mutation size (y) at generation (x)"
    captions["plot-output-singlevalue-fitness_mean.bin.Rdata.png"] = "TODO"
    captions["plot-output-singlevalue-fitness_stdev.bin.Rdata.png"] = "TODO"
    captions["plot-output-singlevalue-no_offspring.bin.Rdata.png"] = "TODO"
    captions["plot-output-singlevalue-phenotype_total_mean.bin.Rdata.png"] = "TODO"
    captions["plot-output-singlevalue-phenotype_stdev.bin.Rdata.png"] = "TODO"

    if image in captions:
        return captions[image]
    else: 
        return "TODO - no caption ready"
   
class TEImage:
    def __init__(self, num, filename, caption, shortname):
        self.num = num
        self.filename = filename
        self.caption = caption
        self.shortname = shortname

def get_images_list(active_TE, inactivation, deautonom):
    num = 0
    final_list = []
    core_plots_filenames = ["plot-3.png",
        "plot-output-singlevalue-environmental_change.bin.Rdata.png",
	"plot-output-singlevalue-avg_mutations.bin.Rdata.png",
	"plot-output-singlevalue-fitness_mean.bin.Rdata.png",
	"plot-output-singlevalue-fitness_stdev.bin.Rdata.png",
	"plot-output-singlevalue-no_offspring.bin.Rdata.png",
	"plot-output-singlevalue-phenotype_total_mean.bin.Rdata.png",
	"plot-output-singlevalue-phenotype_stdev.bin.Rdata.png"]
    core_list = []
    for filename in core_plots_filenames : 
        core_list.append(TEImage(num, filename, get_image_caption(filename), ""))
        num += 1
    final_list += [(1, "Basic plots", core_list)]

    if active_TE :
        active_plots_filenames = [#"plot-mean-aut-copy-number.png",
	    #"plot-mean-copy-number.png",
	    #"plot-mean-nonaut-copy-number.png",
	    #"plot-stdev-copy-number.png",
	    "plot-output-singlevalue-aut_TE_stdev.bin.Rdata.png",
	    "plot-output-singlevalue-aut_TE_var.bin.Rdata.png",
	    "plot-output-singlevalue-aut_transposons.bin.Rdata.png", 
            "plot-output-singlevalue-selection_gradient_aut_TEs.bin.Rdata.png"]
        active_list = []
        for filename in active_plots_filenames : 
            active_list.append(TEImage(num, filename, get_image_caption(filename), ""))
            num += 1
        final_list += [(1, "Active TEs", active_list)]
    else :
        final_list += [(0, "", [])]


    if inactivation :
        inactive_plots_filenames = ["plot-output-singlevalue-inactive_TE_stdev.bin.Rdata.png",
	    "plot-output-singlevalue-inactive_TE_var.bin.Rdata.png",
	    "plot-output-singlevalue-inactive_transposons.bin.Rdata.png", 
            "plot-output-singlevalue-selection_gradient_inactive_TEs.bin.Rdata.png"]
    
        inactive_list = []
        for filename in active_plots_filenames : 
            inactive_list.append(TEImage(num, filename, get_image_caption(filename), ""))
            num += 1
        final_list += [(1, "Inactive TEs", inactive_list)]
    else :
        final_list += [(0, "", [])]


    if deautonom :
        nonaut_plots_filenames = ["plot-output-singlevalue-nonaut_TE_stdev.bin.Rdata.png",
	    "plot-output-singlevalue-nonaut_TE_var.bin.Rdata.png",
	    "plot-output-singlevalue-nonaut_transposons.bin.Rdata.png", 
            "plot-output-singlevalue-selection_gradient_nonaut_TEs.bin.Rdata.png"]
        deaut_list = []
        for filename in active_plots_filenames : 
            deaut_list.append(TEImage(num, filename, get_image_caption(filename), ""))
            num += 1
        final_list += [(1, "Non-autonomous TEs", deaut_list)]
    else :
        final_list += [(0, "", [])]


    #final_list = []
    #images_list = []
    #for num, filename in enumerate(core_plots_filenames) : 
    #    images_list.append(TEImage(num, filename, get_image_caption(filename), ""))
    #final_list.append((1, images_list))
    #return images_list
    return final_list



