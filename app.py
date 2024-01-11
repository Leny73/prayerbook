from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://lyuben:temp123!@localhost:5432/prayerbook'

db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    prayerorders = db.relationship("PrayerOrder", back_populates="student")

class Formula(db.Model):
    __tablename__ = 'formulas'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=False)
    bookPage = db.Column(db.Integer, nullable=False)
    prayerorder_id = db.Column(db.Integer, db.ForeignKey('prayerorders.id'))
    prayerorder = db.relationship("PrayerOrder", back_populates="formulas")
    def format(self):
        return {
        'id': self.id,
        'text': self.text,
        'bookPage': self.bookPage,
        }

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    bookPage = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String())
    prayerorder_id = db.Column(db.Integer, db.ForeignKey('prayerorders.id'))
    prayerorder = db.relationship("PrayerOrder", back_populates="songs")
    def format(self):
        return {
        'id': self.id,
        'text': self.text,
        'name': self.name,
        'bookPage': self.bookPage,
        'type': self.type
        }

class Psalm(db.Model):
    __tablename__ = 'psalms'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    bookPage = db.Column(db.Integer, nullable=False)
    prayerorder_id = db.Column(db.Integer, db.ForeignKey('prayerorders.id'))
    prayerorder = db.relationship("PrayerOrder", back_populates="psalms")
    def format(self):
        return {
        'id': self.id,
        'text': self.text,
        'name': self.name,
        'bookPage': self.bookPage,
        }

class Prayer(db.Model):
    __tablename__ = 'prayers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    text = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    bookPage = db.Column(db.Integer, nullable=False)
    prayerorder_id = db.Column(db.Integer, db.ForeignKey('prayerorders.id'))
    prayerorder = db.relationship("PrayerOrder", back_populates="prayers")
    def format(self):
        return {
        'id': self.id,
        'text': self.text,
        'name': self.name,
        'bookPage': self.bookPage,
        'completed': self.completed
        }


class PrayerOrder(db.Model):
    __tablename__='prayerorders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = db.relationship("Student", back_populates="prayerorders")

    prayers = db.relationship("Prayer", back_populates="prayerorder")
    songs = db.relationship("Song", back_populates="prayerorder")
    formulas = db.relationship("Formula", back_populates="prayerorder")
    psalms = db.relationship('Psalm', back_populates="prayerorder")

db.create_all()

ENTRIES_PER_SHELF = 10

def paginate_entries(request, entries):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * ENTRIES_PER_SHELF
    end = start + ENTRIES_PER_SHELF

    formatted_entries = [entry.format() for entry in entries]
    current_entries = formatted_entries[start:end]
    return current_entries

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

@app.route('/prayers', methods=['GET'])
def get_prayers():
    prayers = Prayer.query.order_by(Prayer.id).all()
    current_entries = paginate_entries(request, prayers)

    if len(current_entries) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'prayers': current_entries,    
            'total': len(Prayer.query.all())
        })

@app.route('/songs', methods=['GET'])
def get_songs():
    songs = Song.query.order_by(Song.id).all()
    current_entries = paginate_entries(request, songs)

    if len(current_entries) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'songs': current_entries,    
            'total': len(Prayer.query.all())
        })

@app.route('/psalms', methods=['GET'])
def get_psalms():
    psalms = Psalm.query.order_by(Psalm.id).all()
    current_entries = paginate_entries(request, psalms)

    if len(current_entries) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'psalms': current_entries,    
            'total': len(Psalm.query.all())
        })

@app.route('/formulas', methods=['GET'])
def get_formulas():
    formulas = Formula.query.all()
    current_entries = paginate_entries(request, formulas)

    if len(current_entries) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'formulas': current_entries,    
            'total': len(Formula.query.all())
        })

@app.route('/all-data', methods=['GET'])
def get_all_data():
    formulas = Formula.query.order_by(Formula.id).all()
    psalms = Psalm.query.order_by(Psalm.id).all()
    songs = Song.query.order_by(Song.id).all()
    prayers = Prayer.query.order_by(Prayer.id).all()

    all_data = [formulas, psalms, songs, prayers]
    all_data_formatted = []
    for data in all_data:
        all_data_formatted.append(paginate_entries(request, data))

    if len(all_data_formatted) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'data': all_data_formatted,
        })



@app.route('/search')
def search_data():
  search_term = request.form['search_term']
  search = "%{}%".format(search_term)
  prayers = Prayer.query.filter(Prayer.name.ilike(search)).all()
  prayerList = []
  for prayer in prayers:
    prayerList.append({
        "id": prayer.id,
        "name": prayer.name,
        "body": prayer.text
    })

  response= {
    "count": len(prayers),
    "data": prayerList
  }
  return response