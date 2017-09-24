from index import db

class Task(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    param1 = db.Column(db.Integer)
