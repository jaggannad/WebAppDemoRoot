from class_files import modal

app = modal.localPackages.Flask(__name__)
app.secret_key = "FlaskDemo"


@app.route('/')
def index():
    return modal.localPackages.redirect('/about')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if modal.localPackages.request.method == "POST":
            name = modal.localPackages.request.form['name']
            email = modal.localPackages.request.form['email']
            password = modal.localPackages.request.form['password']
            if modal.UserInfo.query().filter(modal.UserInfo.email == email).get():
                modal.localPackages.flash("Email already exists, Try a different Email")
            else:
                user_key = modal.UserInfo(username=name, email=email, password=password, profilepic="default.jpg").put()
                if user_key:
                    return modal.localPackages.redirect(modal.localPackages.url_for('login', message="registrationSuccessful"))
                else:
                    modal.localPackages.flash("Oops! Something went wrong. Please try again after some time.")
    except Exception, Value:
        modal.localPackages.flash(Value)
    return modal.localPackages.render_template('register.html')


@app.route('/login/v1.1/<message>', methods=['GET', 'POST'])
def login(message):
    error = ''
    try:
        if modal.localPackages.request.method == 'POST':
            req_email = modal.localPackages.request.form['email']
            req_password = modal.localPackages.request.form['password']
            get_user_info = modal.UserInfo.query().filter(modal.UserInfo.email == req_email).get()

        # Check if the inputs match
            if get_user_info and get_user_info.password == req_password:
                user_info = {'name': get_user_info.username, 'password': get_user_info.password, 'profilepic': get_user_info.profilepic}
                modal.localPackages.session['user'] = user_info
                return modal.localPackages.redirect(modal.localPackages.url_for('profile', username=user_info.get('name')))
            else:
                error = "Invalid Credentials! Pls try again."
                modal.localPackages.flash(error)

        return modal.localPackages.render_template("login.html", message=error)
    except Exception, value:
        modal.localPackages.flash(str(value)+" in except block")
    modal.localPackages.flash(message+" Please login to continue!")
    return modal.localPackages.render_template("login.html", message=value)


@app.route('/logout/<username>')
def logout(username):
    modal.localPackages.session.pop('user', None)
    return modal.localPackages.redirect(modal.localPackages.url_for('login', message=username+"Loggedout"))


@app.route('/about')
def about():
    modal.localPackages.flash("Hi there!")
    return modal.localPackages.render_template('aboutus.html')


@app.route('/profile/v1.1/userprofile/<username>/LoggedIn', methods=['GET', 'POST'])
def profile(username):
    recent_posts = modal.Post.query().order(-modal.Post.timestamp)
    return modal.localPackages.render_template("profile.html", username=username, issinfo=modal.issinfo,
                                               weatherinfo=modal.weather, recent_posts=recent_posts)


@app.route('/post/<username>', methods=['GET', 'POST'])
def post(username):
    response = {'success': True, 'desc': 'Posted Message', 'timestamp': str(modal.localPackages.datetime.datetime.now())}
    if modal.localPackages.request.method == 'POST':
        text = modal.localPackages.request.form['javascript_data']
        modal.Post(post=text, name=username, likes=0).put()
    else:
        response.update({'success': False, 'desc': 'Post Failed',
                         'timestamp': str(modal.localPackages.datetime.datetime.now())})
    return modal.localPackages.jsonify(response)


@app.route('/like/<key>', methods=['GET', 'POST'])
def like(key):
    response = {'success': True, 'desc': 'Post Liked', 'timestamp': str(modal.localPackages.datetime.datetime.now())}
    if modal.localPackages.request.method == 'POST':
        post = modal.localPackages.ndb.Key(urlsafe=key).get()
        if post:
            post.likes = post.likes+1
            post.put()
        else:
            response.update({'success': False, 'desc': 'Post Like Failed', 'timestamp': str(modal.localPackages.datetime.datetime.now())})
    return modal.localPackages.jsonify(response)


@app.route('/update/<key>', methods=['GET', 'POST'])
def update(key):
    response = {'success': True, 'desc': 'Post Updated', 'timestamp': str(modal.localPackages.datetime.datetime.now())}
    if modal.localPackages.request.method == 'POST':
        post = modal.localPackages.ndb.Key(urlsafe=key).get()
        if post:
            post.post = modal.localPackages.request.form['javascript_data']
            post.put()
        else:
            response.update({'success': False, 'desc': 'Post Update Failed',
                             'timestamp': str(modal.localPackages.datetime.datetime.now())})
    return modal.localPackages.jsonify(response)


@app.route('/delete/<key>', methods=['GET', 'POST'])
def delete(key):
    response = {'success': True, 'desc': 'Post Deleted', 'timestamp': str(modal.localPackages.datetime.datetime.now())}
    if modal.localPackages.request.method == 'POST':
        post = modal.localPackages.ndb.Key(urlsafe=key).get()
        if post:
            post.key.delete()
        else:
            response.update({'success': False, 'desc': 'Post Delete Failed',
                             'timestamp': str(modal.localPackages.datetime.datetime.now())})
    return modal.localPackages.jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)


