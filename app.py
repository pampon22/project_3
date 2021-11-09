from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'somesecretkey'


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='Ben', password='password'))
users.append(User(id=2, username='Philip', password='123456'))
users.append(User(id=3, username='Naser', password='software'))

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('home'))

        return redirect(url_for('login'))

    return render_template('login.html')



# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
dbase = SQLAlchemy(app)


class Todo(dbase.Model):
    id = dbase.Column(dbase.Integer, primary_key=True)
    title = dbase.Column(dbase.String(100))
    complete = dbase.Column(dbase.Boolean)


@app.route("/")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list, date =datetime)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    dbase.session.add(new_todo)
    dbase.session.commit()
    return redirect(url_for("home"))


@app.route("/check/<int:todo_id>")
def check(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = True
    dbase.session.commit()
    return redirect(url_for("home"))


@app.route("/uncheck/<int:todo_id>")
def uncheck(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = False
    dbase.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    dbase.session.delete(todo)
    dbase.session.commit()
    return redirect(url_for("home"))



if __name__ == "__main__":
    dbase.create_all()
    app.run(debug=True)


