#!/bin/bash
source webservice/bin/activate
export FLASK_APP=index.py



webservice/bin/flask db init
webservice/bin/flask db migrate
webservice/bin/flask db upgrade
