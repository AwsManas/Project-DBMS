from flask import Flask , request , render_template, redirect , url_for, session
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

mysql = MySQL(app)

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
                return "You entered a wrong password! Please Reload"   
        else:
            return "You entered a new username! Please Reload"         
    return render_template("login.html")
@app.route('/fillsubjects',methods = ['GET','POST'])
def fillsubjects():
   # if 'usn' not in session:
    #    return redirect( url_for('login'))
    #else:
     #   usn = session['usn']    
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
    return render_template("fillsubs2.html")
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
            return redirect(url_for('attendence'))
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
if __name__ == "__main__":
    app.run(debug=True)