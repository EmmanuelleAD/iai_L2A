import os
from flask import abort
from dotenv import load_dotenv
from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
load_dotenv()
mdp=os.getenv('password')
#production nvelle env systeme
app = Flask(__name__)

#motdepasse = quote_plus('caleb1234')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:{}@localhost:5432/bdetudiant'.format(mdp)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Etudiant(db.Model):
    __tablename__='etudiants'
    id=db.Column(db.Integer,primary_key=True)
    nom=db.Column(db.String(100),nullable=False)
    adresse=db.Column(db.String(100),nullable=True)
    email=db.Column(db.String(100),unique=False)
    def __init__(self,nom,adresse,email):
        self.nom=nom
        self.adresse=adresse
        self.email=email

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return{
            'id':self.id,
            'nom':self.nom,
            'adresse':self.adresse,
            'email':self.email
        }

db.create_all()
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success':False,'error': 404,'message': 'not found'}),404

@app.errorhandler(400)
def server_error(error):
    return jsonify({'success':False,'error': 400,'message': 'not found'}),400
@app.route('/')
def index():
    abort(404)

@app.route('/etudiants',methods=['GET'])
def get_all_students():
    etudiants=Etudiant.query.all()
    formated_students = [etudiant.format() for etudiant in etudiants]
    return jsonify({
        'success':True,
        'etudiant':formated_students,
        'total':Etudiant.query.count()
    })

@app.route('/etudiants',methods=['POST'])
def add_student():
    body=request.get_json()
    new_nom = body.get('nom',None)
    new_email=body.get('email',None)
    new_adresse=body.get('adresse',None)
    #if new_adresse is None or new_email:
    et=Etudiant(nom=new_nom,email=new_email,adresse=new_adresse)
    et.insert()
    etudiants=Etudiant.query.all()
    etudiant_formated=[etudiant.format() for etudiant in etudiants]
    return jsonify({
        'created_id':et.id,
        'success':True,
        'Total':len(Etudiant.query.all()),
        'etudiants':etudiant_formated
    })
@app.route('/etudiants/<int:id>',methods=['GET'])
def get_one_student(id):
    try:
        et=Etudiant.query.get(id)
        #et=Etudiant.query.filter(Etudiant.id==id).first()
        if et is None:
            abort(404)
        else:
            et_formated=et.format()
            return jsonify({
                'asked_student':et_formated,
                'asked_id':id,
                'success':True
            })
    except:
        abort(400)

@app.route('/etudiants/<int:id>', methods=['DELETE'])
def del_one_student(id):
    etudiant= Etudiant.query.get(id)
    if etudiant is None:
       abort(404)
    else:
        etudiant.delete()
        return jsonify({
            "deleted_student":id,
            "success":True,
            "Total":Etudiant.query.count(),
            "deleted_student":etudiant.format()
        })

@app.route('/etudiants/<int:id>',methods=['PATCH'])
def update_student(id):
    body=request.get_json()
    etudiant=Etudiant.query.get(id)
    etudiant.nom=body.get("nom",None)
    etudiant.adresse=body.get("adresse",None)
    etudiant.email=body.get("email",None)

    if etudiant.nom is None or etudiant.adresse is None or etudiant.email is None:
        abort(400)
    else:
        etudiant.update()
        return jsonify({
            "success":True,
            "Updated_id":id,
            "Updated_student":etudiant.format()
        })

if __name__=='__main__':
    app.run(debug=True)
