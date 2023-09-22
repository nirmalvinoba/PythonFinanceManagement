from flask import Flask,render_template,request,redirect,url_for,session
import requests
import sqlite3 as sql

app = Flask(__name__)

bank = "https://api.mfapi.in/mf/"
app.secret_key = "Niru123"



def isloggedin():
    return "username" in session
    
@app.route('/base')
def base():
    return render_template ("base.html")

@app.route('/', methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("user")
        password = request.form.get("pass")
        con = sql.connect("user.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("select * from signup where username=? and password=?", (username,password))
        data = cur.fetchall()
        for  i in data:
            if username in i and password == i[1]:
                session["username"] = username
                return redirect (url_for('home'))

        # if username in userdetails and password == userdetails.get(username):
        #     session["username"] = username
        #     return redirect (url_for('home'))
            else:
                return "Incorrect Username or Password"
    return render_template ("login.html")

@app.route('/signup', methods = ["GET","POST"])
def signup():
    if request.method == "POST":
        name1 = request.form.get("username")
        pass1 = request.form.get("password")
        con = sql.connect("user.db")
        cur = con.cursor()
        cur.execute("insert into signup (username,password) values(?,?)",
                        (name1,pass1))
        con.commit()
        return redirect (url_for('login'))
    return render_template ("signup.html") 



@app.route('/home')
def home():
    list_1 = []
    if "username" in session:
        con = sql.connect("user.db")
        cur = con.cursor()
        cur.execute("select * from crud")
        fet = cur.fetchall()
        for i in fet:
            id = i[0]
            name = i[1]
            funds = i[2]
            inves = i[3]
            units = i[4]
            completeurl = requests.get(bank + str(funds))
            dict_1 = {}
            dict_1["SNO"] = id
            dict_1["Name"] = name
            dict_1["Fundname"] = completeurl.json().get("meta").get("fund_house")
            dict_1["Invested"] = inves
            dict_1["Unitsheld"] = units
            dict_1["Nav"] = completeurl.json().get("data")[0].get("nav")
            dict_1["Currentvalue"] = float(dict_1.get("Nav"))*dict_1.get("Invested")
            dict_1["Growth"] = float(dict_1.get("Currentvalue"))-dict_1.get("Unitsheld")
            list_1.append(dict_1)
        return render_template ("home.html", box = list_1)
    return render_template("home.html")

@app.route('/insert', methods = ["GET","POST"])
def insert():
    if request.method == "POST":
        con = sql.connect("user.db")
        cur = con.cursor()
        cur.execute("insert into crud (Name,Funds,Invested,Unitsheld) values (?,?,?,?)",
                    (request.form.get("name"),request.form.get("funds"),
                    request.form.get("inves"),request.form.get("units")))
        con.commit()
        # return redirect (url_for('home'))
        return redirect (url_for('home'))
    return render_template ("add_user.html")

@app.route('/edit/<string:id>', methods = ["GET","POST"])
def edit(id):
    if request.method == "POST":
        con = sql.connect("user.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("update crud set Name=?,Funds=?,Invested=?,Unitsheld=? where ID=?",
                    (request.form.get("name"),request.form.get("funds"),
                    request.form.get("inves"),request.form.get("units"),id))
        fet=cur.fetchall()
        con.commit()

        return redirect (url_for('home'))
    conn= sql.connect("user.db")
    conn.row_factory=sql.Row
    curr = conn.cursor()
    curr.execute("select * from crud where ID=?",(id,))
    fet = curr.fetchone()
    return render_template ("edit_user.html", bag=fet)

@app.route('/delete/<string:id>')
def delete(id):
    con = sql.connect("user.db")
    cur = con.cursor()
    cur.execute("delete from crud where ID=?",(id,))
    con.commit()
    return redirect (url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
