#!/usr/bin/python
import sys
import time
import sqlite3
import subprocess

def set_simulation_status(status, task_ID):

    try: 
        con = sqlite3.connect(  'TEmodelDB.sqlite3',
                            detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        cur.execute("UPDATE Task SET simulation_status = '" + status + "' WHERE id = " + task_ID + ";")
        print(con)
        con.commit() 
        print("I have set the status to:" + status)
    except Exception as e: 
        print(e)
        print("I had a problem with access to the database")
   

def main(myargs):
    print(myargs)
    time.sleep(1)
    task_ID = myargs[0]
        
    # set model folder 
    HOST = "transp@wloczykij"
    
    # Ports are handled in ~/.ssh/config since we use OpenSSH
    # create simulations folder
    # create parameters.py
    COMMAND = "'/home/transp/simulations/webservice/generate-parameters-file.py " + task_ID + "'"

    try: 
        ssh = subprocess.Popen("ssh transp@wloczykij " + COMMAND,
                       shell = True,
                       stdout = subprocess.PIPE,
                       stderr = subprocess.PIPE)
        result, errs = ssh.communicate()
        print("From program.py out: " + result)
        print("From program.py err: " + errs)
      
        with open("program.log", "w+") as f:
            f.write(result)
            f.write(errs)
    except Exception as e:
        set_simulation_status("Error", task_ID)
        print(e)
    

    
    # run simulation 
    # result = sum(map(int, myargs[1:])) 

    # store results
    
    # remove simulations folder

    # update database entry
    set_simulation_status("Complete", task_ID)
    
    

if __name__ == "__main__": 
    main(sys.argv[1:])
