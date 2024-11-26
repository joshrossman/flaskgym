from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields,validate, ValidationError


    

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:rootPassword1919@localhost/fitness_center'
db=SQLAlchemy(app)
ma=Marshmallow(app)

class MemberSchema(ma.Schema):
    id=fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields=('id','name','age')

class WorkoutSchema(ma.Schema):
    session_id=fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ('session_id','member_id','session_date','session_time','activity')

member_schema=MemberSchema()
members_schema=MemberSchema(many=True)
workout_schema=WorkoutSchema()
workouts_schema=WorkoutSchema(many=True)


class Member(db.Model):
    __tablename__="members"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    workouts = db.relationship('WorkoutSession',backref="members")

class WorkoutSession(db.Model):
    __tablename__='workoutsessions'
    session_id=db.Column(db.Integer,primary_key=True)
    member_id= db.Column(db.Integer,db.ForeignKey('members.id'))
    session_date=db.Column(db.Date,nullable=False)
    session_time=db.Column(db.String(50),nullable=False)
    activity=db.Column(db.String(200),nullable=False)
    

with app.app_context():
    db.create_all()

@app.route('/members',methods=['GET'])
def get_member():
    members=Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=["POST"])
def add_member():
    try:
        member_data=member_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":f'{e}'}),400
    new_member = Member(id=member_data['id'],name=member_data['name'],age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message":"new member added"}),201

@app.route('/members/<int:id>',methods=["DELETE"])
def delete_members(id):
    member_to_delete=Member.query.get_or_404(id)
    db.session.delete(member_to_delete)
    db.session.commit()
    return jsonify({"message":"member succesfully deleted"}),201

@app.route('/workoutsessions',methods=["POST"])
def add_session():
    try:
        workout_data=workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error":f"{e.messages}"}),404
    new_session=WorkoutSession(session_id=workout_data['session_id'],member_id=workout_data["member_id"],session_date=workout_data['session_date'],session_time=workout_data['session_time'],activity=workout_data['activity'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message":"session added succesfully"}),201

@app.route('/workoutsessions',methods=["GET"])
def get_sessions():
    workout_data=WorkoutSession.query.all()
    return workouts_schema.jsonify(workout_data)

@app.route('/workoutsessions/<int:id>',methods=['PUT'])
def update_sessions(id):
    session=WorkoutSession.query.get_or_404(id)
    try:
        session_data=workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"Error":f'{e.messages}'})
    
    session.session_id=session_data['session_id']
    session.member_id =session_data['member_id']
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']

    db.session.commit()
    return jsonify(({"message":"session information updated."})),201

@app.route('/mysession/by-name', methods=['GET'])
def search_by_member():
    id=request.args.get('id')
    workoutsessions=WorkoutSession.query.filter_by(member_id=id).all()
    if workoutsessions:
        return workouts_schema.jsonify(workoutsessions)
    else:
        return jsonify({"message":"Nothing found by search"}),500

if __name__=='__main__':
    app.run(debug=True)
