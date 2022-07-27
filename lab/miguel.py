from enum import unique
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


basedir =os.path.abspath(os.path.dirname(__file__))
file_name = ''.join(list(__file__)[:-3])

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, file_name+'.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


########### Models  #########
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='user')


    def __init__(self, username, role):
        self.username = username
        self.role = role
    

    def __repr__(self):
        return f"<User: {self.username}>"



class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)


    def __init__(self, name):
        self.name = name
    

    def __repr__(self):
        return f"<Role: {self.name}>"
    

######## Schemas ########
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'role_id')


class RoleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')


user_sch = UserSchema()
users_sch = UserSchema(many=True)
role_sch = RoleSchema()
roles_sch = RoleSchema(many=True)


##### Routes

### Read
@app.route('/')
def index():
    return jsonify("This is miguel")


@app.route('/users')
def get_users():
    users = User.query.all()
    resp = users_sch.jsonify(users)
    return resp


@app.route('/user/<id>')
def get_user(id):
    usr = User.query.get(id)
    if usr:
        resp = user_sch.jsonify(usr)
        return resp
    else:
        return not_found()


@app.route('/roles')
def get_roles():
    roles = Role.query.all()
    resp = roles_sch.jsonify(roles)
    return resp


# Create
@app.route('/add/user', methods=['POST'])
def add_user():
    username = request.json['username']
    role = request.json['role']

    if username and role and request.method == 'POST':
        rl = Role.query.get(role)
        if rl:
            try:
                user = User(username, rl)
                db.session.add(user)
                db.session.commit()
                resp = user_sch.jsonify(user)
                resp.status = 201
            except:
                resp =  jsonify(f'Internal Server Error')
                resp.status = 500

        else:
            resp = jsonify(f'role does not exist!')
            resp.status = 400

        return resp
    
    else:
        return not_found()


# Update
@app.route('/modify/user/<id>', methods=['PUT'])
def modify(id):
    usr = User.query.get(id)

    if usr:
        data = request.json
        kys = list(data.keys())
        if 'username' in kys and 'role' in kys:
            try:
                role, username= data['role'], data['username']
                rl = Role.query.get(role)
                usr.username = username
                usr.role = rl
                db.session.add(usr)
                db.session.commit()

                resp = user_sch.jsonify(usr)
                # resp.status = 204

            except:
                resp = jsonify('Internal Server Error')
                resp.status = 500

        else:
            resp = jsonify('Username or role not present')
            resp.status = 400

        return resp
    else:
        return not_found()


# Delete
@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    usr = User.query.get(id)

    if usr:
        db.session.delete(usr)
        db.session.commit()
        return jsonify(f'{usr.username} deleted!')
    
    else:
        return not_found()


def not_found():
    resp = jsonify("Error")
    resp.status = 404

    return resp


if __name__ == "__main__":
    app.run()