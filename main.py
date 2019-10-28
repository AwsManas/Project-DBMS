from flask import Flask , request , render_template, redirect , url_for
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'M@nas4life'
app.config['MYSQL_DB'] = 'nie'

mysql = MySQL(app)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        inputvalues = request.form
        name = inputvalues['name']
        usn = inputvalues['USN']
        email = inputvalues['email']
        phone = int(inputvalues['phone_number'])
        sem = int(inputvalues['sem'])
        passw = inputvalues['pass']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO signup VALUES (%s,%s,%s,%s,%s,%s)", (name,usn,email,phone,sem,passw))
        mysql.connection.commit()
        cur.close()
    return render_template("signup.html")
@app.route('/login', methods= ['GET','POST'])
def login():
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
                return redirect( url_for('events') )
            else:
                return "Wrong password"   
        else:
            return "Invald username"         
    return render_template("login.html")
@app.route('/events')
def events():
    return render_template('events.html')    
if __name__ == "__main__":
    app.run(debug=True)