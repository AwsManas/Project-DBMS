from flask import Flask , request , render_template, redirect
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
        inp = request.form
        
        usn = inp['username']
        #pas = inp['pass']
        cur = mysql.connection.cursor()
        cur.execute('SELECT password from signup where usn = %s',usn)
        data = cur.fetchall()
        '''
        cur.close()
        if data:
            if data[0]==pas:
                return "yay"
            else:
                return "nay"    
        '''
        text = "hey" + data[0]
        return text
    return render_template("login.html")
if __name__ == "__main__":
    app.run(debug=True)

