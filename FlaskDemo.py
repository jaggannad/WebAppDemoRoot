from flask import Flask, render_template, redirect, flash, request, url_for, session

user_db = {'j@g.com': {'name': 'jagan', 'password': 'pass'},
           'v@g.com': {'name': 'vasanth', 'password': 'pass'},
           'p@g.com': {'name': 'parthi', 'password': 'pass'}}

app = Flask(__name__)
app.secret_key = "FlaskDemo"


@app.route('/')
def index():
    return redirect('/about')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    try:
        # Check if the method is POST or GET
        if request.method == 'POST':
            req_email = request.form['email']
            req_password = request.form['password']
        # Check if the inputs match
            if req_email in user_db and user_db.get(req_email).get('password') == "pass":
                session['user'] = user_db.get(req_email).get('name')
                return redirect(url_for('profile', username=session['user']))
            else:
                error = "Invalid Credentials! Pls try again."

        return render_template("login.html", error=error)
    except Exception, value:
        flash(str(value)+" in except block")
        return render_template("login.html", error=value)


@app.route('/about')
def about():
    flash("Hi there!")
    return render_template('aboutus.html')


@app.route('/profile/<username>')
def profile(username):
    return render_template("profile.html", username=username)


if __name__ == "__main__":
    app.run(debug=True)
