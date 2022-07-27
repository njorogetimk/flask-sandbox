from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Author Database
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    specialisation = db.Column(db.String(50))

    def __init__(self, name, specialisation):
        self.name = name
        self.specialisation = specialisation
    

    def __repr__(self):
        return f"<Product {self.name}, {self.specialisation}>"


class AuthorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'specialisation')


auth_sch = AuthorSchema()
auths_sch = AuthorSchema(many=True)

@app.route('/')
def main():
    return jsonify({"hello": 'Hello there Flask!'})

# Read
@app.route('/authors')
def get_authors():
    auths = Author.query.all()

    return auths_sch.jsonify(auths)

@app.route('/author/<name>')
def get_author(name):
    auth = Author.query.filter_by(name=name).first()
    return auth_sch.jsonify(auth)

# Create
@app.route('/author/', methods=['GET','POST'])
def add_author():
    author = request.json['name']
    specs = request.json['spec']
    
    auth = Author(author, specs)
    
    db.session.add(auth)
    db.session.commit()
    
    return auth_sch.jsonify(auth)


# Update
@app.route('/author/update', methods=['PUT'])
def rename_specs():
    name = request.json['name']
    specs = request.json['spec']

    auth = Author.query.filter_by(name=name).first()
    auth.specialisation = specs

    db.session.add(auth)
    db.session.commit()

    return auth_sch.jsonify(auth)

# Delete
@app.route('/author/', methods=['DELETE'])
def del_author():
    name = request.json['name']

    auth = Author.query.filter_by(name=name).first()
    
    db.session.delete(auth)
    db.session.commit()

    return auth_sch.jsonify(auth)


if __name__ == '__main__':
    app.run()