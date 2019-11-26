from flask import Flask , request , render_template, redirect , url_for, session,flash
import datetime
from datetime import date
from flask_mail import Message, Mail
import json
from flask_mysqldb import MySQL
import yaml
db = yaml.load(open('.gitignore/db.yaml'))
app = Flask(__name__)
app.secret_key = 'manas'
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'proj.nie.12@gmail.com'
app.config['MAIL_PASSWORD'] = "nie123456"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mysql = MySQL(app)
mail = Mail(app)

@app.route('/signup',methods=['GET','POST'])
def index():
    if request.method=='POST':
        inputvalues = request.form
        name = inputvalues['name']
        usn = inputvalues['USN']
        email = inputvalues['email']
        phone = int(inputvalues['phone_number'])
        sem = int(inputvalues['sem'])
        sec = inputvalues['sec']
        passw = inputvalues['pass']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO signup VALUES (%s,%s,%s,%s,%s,%s,%s)", (name,usn,email,phone,sem,sec,passw))
        mysql.connection.commit()
        cur.close()
        session['usn'] = usn
        return redirect( url_for('fillsubjects'))
    return render_template("signup.html")
@app.route('/login', methods= ['GET','POST'])
def login():
    session.pop('usn', None)
    if request.method=='POST':
        data = None
        inp = request.form
        usn = inp['username']
        pas = inp['pass']
        cur = mysql.connection.cursor()
        cur.execute('SELECT password from signup where usn = %s',[str(usn)])
        data = cur.fetchall()
        cur.close()
        if data:
            if data[0][0]==pas:
                session['usn']=usn
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials")
        else:
            flash("Invalid credentials")         
    return render_template("login.html")
@app.route('/fillsubjects',methods = ['GET','POST'])
def fillsubjects():
    if 'usn' not in session:
        return redirect( url_for('login'))
    else:
        usn = session['usn']    
    if request.method=='POST':
        inp = request.form
        for i in range (int(inp['num'])):
            filename = "sub" + str(i+1)
            catten = filename + "c"
            tatten = filename + "t"
            courcecode = inp[filename]
            curattend = int(inp[catten])
            totalattend = int(inp[tatten])
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO subjects VALUES (%s,%s,%s,%s)", (usn,courcecode,curattend,totalattend))
            mysql.connection.commit()
            cur.close()
        return redirect(url_for('home'))
    return render_template("fillsubs3.html")
@app.route('/selectclass', methods = ['GET','POST'])
def select():
    if 'teacher' not in session:
        return redirect (url_for('login_t'))
    cur = mysql.connection.cursor()
    cur.execute("select distinct subjectcode from subjects")
    result1 = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("select distinct sec  from signup")
    result2 = cur.fetchall()
    cur.close()
    if request.method=='POST':
        inp = request.form
        sub = inp['subs']
        sec = inp['sec']
        session['sub'] = sub
        session['sec'] = sec 
        return redirect(url_for('attendence'))     
    return render_template("select2.html",subjects = result1,sections = result2)               
@app.route('/atten',methods = ['GET','POST'])
def attendence():
    if 'sec'  not in session or 'sub' not in session:
        return redirect(url_for('select'))
    sec = session['sec']
    sub = session['sub']
    cur = mysql.connection.cursor()
    cur.execute('select name,s.usn from signup s , subjects u where  s.sec = %s and u.subjectcode = %s and s.usn = u.usn order by s.name',(sec,sub))
    result = cur.fetchall()
    cur.close()
    if request.method=='POST':
        session.pop('sec',None)
        session.pop('sub',None)
        inp = request.form
        for d in inp:
            usn = str(d)
            cur = mysql.connection.cursor()
            cur.execute('update subjects set present = present + 1 where usn = %s and subjectcode = %s ',(usn,sub))
            mysql.connection.commit()
            cur.close()    
        cur = mysql.connection.cursor()
        cur.execute('UPDATE subjects s join signup u on s.usn = u.usn set s.total = s.total + 1 where s.subjectcode = %s and u.sec = %s;',(sub,sec))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))
    return render_template('atten.html',attendance =  result)        
@app.route('/home')
def home():
    return  render_template('home.html')
@app.route('/teacherlogin',methods = ['GET','POST'])
def login_t():
    if 'teacher' in session:
        session.pop('teacher',None)
    if 'usn' in session:
        session.pop('usn',None)
    if request.method=='POST':
        inp = request.form
        pas = inp['pass']
        if pas == 'admin':
            session['teacher'] = 1
            return redirect(url_for('select'))
        else:
            return "Wrong password entered please reload"        
    return render_template('tlogin.html') 
@app.route('/logout')
def logout():
    if 'teacher' in session:
        session.pop('teacher',None)
    if 'usn' in session:
        session.pop('usn',None)
    return redirect(url_for('home'))
@app.route('/stats')
def stats():
    labels = ["I Year" , "II Year","III Year","IV Year"]
    values = []
    
    return render_template("stats.html")  
@app.route('/cgpaCalc', methods = ['GET', 'POST'])
def sfg(): 
    if 'usn' in session:
        cgpa = ''
        if request.method == "POST":
            grade=[]
            cred=[]
            gp=[]
            for i in range(1,10):
                grade.append(request.form['Grade'+str(i)])
                cred.append(float(request.form['cred'+str(i)]))
            for i in range(0,9):
                if grade[i] == "S":
                    gp.append(10.0)
                elif grade[i] == "A":
                    gp.append(9.0)
                elif grade[i] == "B":
                    gp.append(8.0)
                elif grade[i] == "C":
                    gp.append(7.0)
                elif grade[i] == "D":
                    gp.append(6.0)
                else:
                    gp.append(0.0)
            sum1 = 0
            for i in range(0,9):
                sum1 = sum1 + (gp[i]*cred[i])
            tot = 0
            for x in cred:
                tot = tot+x
            cgpa = sum1/tot
            cgpa = round(cgpa,2)
            return render_template('CGPA.html', cgpa=cgpa)
        return render_template('CGPA.html', cgpa=cgpa)
    else:
        return redirect(url_for('home'))
@app.route('/creategroup', methods = ['GET', 'POST'])
def creategroup():
    if 'usn' in session: 
        if request.method == 'POST':
            sub = request.form['sub']
            maxno = request.form['max']
            usn = session['usn']
            cur  = mysql.connection.cursor()
            cur.execute('insert into study(subject,maxno,curno,leader) values(%s, %s, 0, %s)',(sub, maxno, usn))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('groups'))
        return render_template('create.html') 
    else:
        return redirect(url_for('login'))

@app.route('/groups')
def groups():
    if 'usn' in session: 
        cur = mysql.connection.cursor() #creates a cursor that points to the database
        groups = cur.execute("select * from study") #fetches the number of rows in the table
        if groups:
            group_details = cur.fetchall()# Fetches all the rows in the table
        else:
            group_details = "No Groups Available."
        return render_template('groups2.html', groups = group_details)
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)