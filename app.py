import cv2
from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import OMR_Main as omr
from sqlalchemy import Engine, create_engine, select,update
from werkzeug.utils import secure_filename
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['USERNAME']=''
app.config['Score']=0
app.config['SHEET']=0
app.config['Count']=0


app.config['LOGIN_STATUS_F']=False
app.config['LOGIN_STATUS']=False
database=pd.read_csv('static/mp1.csv')
emails=list(database['Email'])
passwords=list(database['Password'])
names=list(database['Name'])
roll=list(database['Roll_NO'])
credentials={}

for i in range(len(emails)):
    credentials[emails[i]]=passwords[i]
print(credentials)
app.config['UPLOAD_FOLDER']=r'static/sheets'

class Roll_Call_List(db.Model):
    name= db.Column(db.String, primary_key=False,nullable=False)
    email=db.Column(db.String, primary_key=False,nullable=False)
    roll = db.Column(db.String, primary_key=True,nullable=False)
    password=db.Column(db.String, primary_key=False,nullable=False)
    score=db.Column(db.String, primary_key=False,nullable=True)
    answersheet=db.Column(db.String, primary_key=False,nullable=True)
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=(request.form['pass'])
        user = Roll_Call_List.query.filter_by(email=email).first()

        if user:
            tag=''
            with db.engine.connect() as conn:
                result = conn.execute(select(Roll_Call_List.password).where(Roll_Call_List.email==email))
                passw=(str(result.all()[0][0]))
                name = conn.execute(select(Roll_Call_List.name).where(Roll_Call_List.email==email)).all()[0][0]
                score=conn.execute(select(Roll_Call_List.score).where(Roll_Call_List.email==email)).all()[0][0]
                sheet=conn.execute(select(Roll_Call_List.answersheet).where(Roll_Call_List.email==email)).all()[0][0]
                
            print(password,name,score)

            if passw==password:
                app.config['LOGIN_STATUS']=True
                app.config['USERNAME']=(str(name))
                app.config['Score']=score
                app.config['SHEET']=sheet
                return redirect('/stud')
            
            else:
                app.config['USERNAME']=''
                tag="Wrong password"
                return render_template('login.html',alrmsg=tag)
            
        else:
            tag='No such User Exists! Please Register Yourself!'
            return render_template('login.html',alrmsg=tag)
        
    else:
        return render_template('login.html')

@app.route("/login_f",methods=['GET','POST'])
def login_f():
    if request.method=="POST":
        email=request.form['email']
        password=int(request.form['pass'])
        if email=='kedar@gmail.com' and password==1234:
            app.config['LOGIN_STATUS_F']=True
            app.config['Count']=1
            return redirect('/facu')
    else:
        return render_template('login_f.html')
    
@app.route("/stud")
def stud():
    if app.config['LOGIN_STATUS']==True:
        print(app.config['SHEET'])
        return render_template('student.html',score=app.config['Score'],sheet=app.config['SHEET'])
    else:
        return redirect('/')

@app.route("/facu",methods=['GET','POST'])
def facu():
    if request.method=="POST":
        q1=int(request.form['q1'])
        q2=int(request.form['q2'])
        q3=int(request.form['q3'])
        q4=int(request.form['q4'])
        q5=int(request.form['q5'])
        omr.ans=[q1-1,q2-1,q3-1,q4-1,q5-1]
        return redirect('/facu2')
        

    elif app.config['LOGIN_STATUS_F']==True:    
        return render_template('facu.html')
    else:
        return redirect('/')

@app.route("/facu2",methods=['GET','POST'])
def facu2():
    if request.method=="POST":
        app.config['Count']=app.config['Count']+1
        img=request.files['img']
        print(type(img))
        roll=int(request.form['roll'])
        img.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(img.filename)))
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(img.filename))
        print(file_path)
        omr.pathImage=str(file_path)
        (score_final,imgFinal)=omr.execute()
        print(type(imgFinal))
        cv2.imwrite("static/checked/myImage"+str(app.config['Count'])+".jpg",imgFinal)
        with db.engine.connect() as conn:
            scre=conn.execute(update(Roll_Call_List).where(Roll_Call_List.roll==roll).values(score=score_final))
            sheet=conn.execute(update(Roll_Call_List).where(Roll_Call_List.roll==roll).values(answersheet=str("static/checked/myImage"+str(app.config['Count'])+".jpg")))
            conn.commit()
        print("Success")
        return render_template('facu2.html',sc=score_final)
        
        # else
            # return 
        # print("Score=",omr.execute())
        # return redirect('/facu2')
    elif app.config['LOGIN_STATUS_F']==True:
        return render_template('facu2.html')
    else:
        return redirect('/')

def tryq():
    app.app_context().push()
    db.create_all()
    for i in range(len(emails)):
        a=Roll_Call_List(name=names[i],email=emails[i],roll=roll[i],password=passwords[i])
        db.session.add(a)
        db.session.commit()

if __name__=='__main__':
    app.run(debug=True,port=2000)
    # tryq()
