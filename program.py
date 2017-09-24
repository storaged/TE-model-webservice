#!/usr/bin/python
import sys
import time
import sqlite3
import subprocess

def main(myargs):
    time.sleep(1)
    task_ID = myargs[0]
        
    # set model folder 
    HOST="transp@wloczykij"
    # Ports are handled in ~/.ssh/config since we use OpenSSH
    COMMAND="./simulations/webservice/generate-parameters-file.py " + task_ID 

    ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()

    # create simulations folder

    # create parameters.py
    
    # run simulation 
    #result = sum(map(int, myargs[1:])) 

    # store results
    
    # remove simulations folder

    # update database entry
   
    con = sqlite3.connect(  'TEmodelDB.sqlite3',
                            detect_types=sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    cur.execute("UPDATE Task SET simulation_status = " + str("complete") + " WHERE id = " + ID + ";")
    con.commit() 

if __name__ == "__main__": 
    main(sys.argv[1:])
