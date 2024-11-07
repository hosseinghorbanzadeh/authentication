from flask import Flask,request,url_for,redirect,render_template,jsonify,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Date
from model import db,User
from flask_bcrypt import Bcrypt
import redis
from flask_session import Session

app=Flask(__name__)

#app.secret_key = "Hossein722GH"
app.config['SECRET_KEY'] = 'the_random_string'
app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://hossein:Passw0rd@localhost/ticket"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SESSION_TYPE']="redis"
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER']=True
app.config['SESSION_REDIS']=redis.from_url('redis://127.0.0.1:6379')
db.init_app(app)

bcrypt=Bcrypt(app)
server_session=Session(app)

with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return "Main Page!!"
@app.route('/register',methods=['POST'])
def register():
    email=request.json['email']
    password=request.json['password']
    user_exists=User.query.filter_by(email=email).first() is not None
    if user_exists:
        return jsonify({"error":"کاربر تکراری است"}),409    
    hashed_password=bcrypt.generate_password_hash(password)
    new_user=User(email=email,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(
        {
            "id":new_user.id,
            "email":new_user.email
        }
    )


@app.route('/login',methods=['POST'])
def login():
    email=request.json['email']
    password=request.json['password']
    user=User.query.filter_by(email=email).first() 
    if user is None:
        return jsonify({"error":"نام کاربری  اشتباه است  "}),409    
    
    if not bcrypt.check_password_hash(user.password,password):
        return jsonify({"error":"کلمه عبور اشتباه است"}),401
    
    session['user_id']=user.id
    return jsonify(
        {
            "id":user.id,
            "email":user.email
        }
    )

@app.route('/@me',methods=['GET'])
def get_curent_user():
    user_id=session.get("user_id")

    if not user_id:
        return jsonify({"خطا":"کاربری شناساس نشد"}),401
    
    user=User.query.filter_by(id=user_id).first() 
    return jsonify(
        {
            "id":user.id,
            "email":user.email
        }
    )



if __name__=="__main__":
    app.run(debug=True)