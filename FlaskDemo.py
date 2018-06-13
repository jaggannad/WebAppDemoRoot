from class_files import modal
import uuid, time

app = modal.localPackages.Flask(__name__)
app.secret_key = "FlaskDemo"

# modal.UserInfo(username="Jagan", id=str(uuid.uuid4()), email="j@g.com", password="pass", profilepic="puppy.jpg", isOnline=False).put()
# modal.UserInfo(username="Parthi", id=str(uuid.uuid4()), email="p@g.com", password="pass", profilepic="mentor.png", isOnline=False).put()
# modal.UserInfo(username="Vasanth", id=str(uuid.uuid4()), email="v@g.com", password="pass", profilepic="hisenberg.jpg", isOnline=False).put()
# modal.UserInfo(username="Lokesh", id=str(uuid.uuid4()), email="l@g.com", password="pass", profilepic="default.jpg", isOnline=False).put()


@app.route('/')
def index():
    if modal.localPackages.session['user'] is not None:
        user_id = modal.localPackages.session['user']['id']
        return modal.localPackages.redirect(modal.localPackages.url_for('profile', userid=user_id))
    return modal.localPackages.redirect('/v1.1/about')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if modal.localPackages.request.method == "POST":
            name = modal.localPackages.request.form['name']
            email = modal.localPackages.request.form['email']
            password = modal.localPackages.request.form['password']
            id = str(uuid.uuid4())
            if modal.UserInfo.query().filter(modal.UserInfo.email == email).get():
                modal.localPackages.flash("Email already exists, Try a different Email")
            else:
                user_key = modal.UserInfo(username=name, id=id, email=email, password=password, profilepic="default.jpg", isOnline=False).put()
                if user_key:
                    return modal.localPackages.redirect(modal.localPackages.url_for('login', message="registrationSuccessful"))
                else:
                    modal.localPackages.flash("Oops! Something went wrong. Please try again after some time.")
    except Exception, Value:
        modal.localPackages.flash(Value)
    return modal.localPackages.render_template('register.html')


@app.route('/login/v1.1/', defaults={'message': None}, methods=['GET', 'POST'])
@app.route('/login/v1.1/<message>', methods=['GET', 'POST'])
def login(message):
    if modal.localPackages.session['user'] is not None:
        user_id = modal.localPackages.session['user']['id']
        return modal.localPackages.redirect(modal.localPackages.url_for('profile', userid=user_id))
    error = ''
    try:
        if modal.localPackages.request.method == 'POST':
            req_email = modal.localPackages.request.form['email']
            req_password = modal.localPackages.request.form['password']
            get_user_info = modal.UserInfo.query().filter(modal.UserInfo.email == req_email).get()

        # Check if the inputs match
            if get_user_info and get_user_info.password == req_password:
                user_info = {
                    'name': get_user_info.username,
                    'id': get_user_info.key.id(),
                    'profilepic': get_user_info.profilepic
                }
                modal.localPackages.session['user'] = user_info
                get_user_info.isOnline = True
                get_user_info.put()
                return modal.localPackages.redirect(modal.localPackages.url_for('profile', userid=user_info.get('id')))
            else:
                error = "Invalid Credentials! Pls try again."
                modal.localPackages.flash(error)

        return modal.localPackages.render_template("login.html", message=error)
    except Exception, value:
        modal.localPackages.flash(str(value)+" in except block")
    modal.localPackages.flash(message+" Please login to continue!")
    return modal.localPackages.render_template("login.html", message=value)


@app.route('/logout/<userid>')
def logout(userid):
    userinfo = modal.UserInfo.query().filter(modal.UserInfo.key == modal.localPackages.ndb.Key(modal.UserInfo, userid)).get()
    userinfo.isOnline = False
    userinfo.put()
    modal.localPackages.session.pop('user', None)
    return modal.localPackages.redirect(modal.localPackages.url_for('login', message=userid+"Loggedout"))


@app.route('/v1.1/about')
def about():
    modal.localPackages.flash("Hi there!")
    return modal.localPackages.render_template('aboutus.html')


@app.route('/profile/v1.1/userprofile/<userid>/LoggedIn', methods=['GET', 'POST'])
def profile(userid):
    userinfo = modal.UserInfo.query().filter(modal.UserInfo.key == modal.localPackages.ndb.Key(modal.UserInfo, userid)).get()
    return modal.localPackages.render_template("profile.html", userid=userid, userinfo=userinfo, issinfo=modal.issinfo,
                                               weatherinfo=modal.weather, modal=modal)


@app.route('/v1.1/newfeed/<userid>', methods=['GET', 'POST'])
def post(userid):
    response = {'success': True,
                'desc': 'Posted Message',
                'timestamp': str(modal.localPackages.datetime.datetime.now())
                }
    if modal.localPackages.request.method == 'POST':
        text = modal.localPackages.request.form['javascript_data']
        userinfo = modal.UserInfo.query().filter(modal.UserInfo.key == modal.localPackages.ndb.Key(modal.UserInfo, userid)).get()
        modal.Globals.newpostkey = modal.Post(post=text, name=userinfo.username, likes=0).put()
        response.update({
            'postid': modal.Globals.newpostkey.urlsafe()
        })
    else:
        response.update({'success': False,
                         'desc': 'Post Failed',
                         'timestamp': str(modal.localPackages.datetime.datetime.now())
                         })
    return modal.localPackages.jsonify(response)


@app.route('/v1.1/feeds/', defaults={'cursor': None})
@app.route('/v1.1/feeds/<cursor>')
def getposts(cursor=None):
    getPostResponse = {
        "success": True,
        "feeds": [],
        "next_cursor": "",
        "more": True
    }
    try:
        cursor = modal.localPackages.Cursor(urlsafe=cursor)
        feeds, next_cursor, more = modal.Post.query().order(-modal.Post.timestamp).fetch_page(4, start_cursor=cursor)
        feedlist = []
        for feed in feeds:
            feedlist.append({
                'key': feed.key.urlsafe(),
                'username': feed.name,
                'post': feed.post,
                'likes': feed.likes,
                'timestamp': feed.timestamp
            })
        if next_cursor is not None:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = 'none'
        getPostResponse.update({
                                'feeds': feedlist,
                                'next_cursor': next_cursor,
                                'more': more
                            })
    except Exception, value:
        modal.localPackages.logging.info(modal.localPackages.format_exc())
        getPostResponse.update({
                                'success': False,
                                'more': False,
                                'desc': 'Server Error: Unable to retrive posts ErrorDesc: {}'.format(value)
                            })
    return modal.localPackages.jsonify(getPostResponse)


@app.route('/v1.1/feedlike/<key>', methods=['GET', 'PUT'])
def like(key):
    response = {
        'success': True,
        'desc': 'Post Liked',
        'timestamp': str(time.time())
    }
    if modal.localPackages.request.method == 'PUT':
        post = modal.localPackages.ndb.Key(urlsafe=key).get()
        if post:
            post.likes = post.likes+1
            post.put()
        else:
            response.update({'success': False,
                             'desc': 'Post Like Failed',
                             'timestamp': str(time.time())
                             })
    return modal.localPackages.jsonify(response)


@app.route('/v1.1/feedupdate/<key>', methods=['GET', 'POST'])
def update(key):
    response = {
        'success': True,
        'desc': 'Post Updated',
        'timestamp': str(time.time())
    }
    if modal.localPackages.request.method == 'POST':
        post = modal.localPackages.ndb.Key(urlsafe=key).get()
        if post:
            post.post = modal.localPackages.request.form['javascript_data']
            post.put()
        else:
            response.update({
                'success': False,
                'desc': 'Post Update Failed',
                'timestamp': str(time.time())
            })
    return modal.localPackages.jsonify(response)


@app.route('/v1.1/feeds/<key>', methods=['GET', 'DELETE'])
def delete(key):
    response = {'success': True,
                'desc': 'Post Deleted',
                'timestamp': str(time.time())
                }
    if modal.localPackages.request.method == 'DELETE':
        post = modal.localPackages.ndb.Key(urlsafe=key).get()
        if post:
            post.key.delete()
        else:
            response.update({
                'success': False,
                'desc': 'Post Delete Failed',
                'timestamp': str(time.time())
            })
    return modal.localPackages.jsonify(response)


@app.route('/v1.1/accountsettings/<userid>', methods=['GET', 'POST'])
def accountsettings(userid):
    userinfo = modal.UserInfo.query(modal.UserInfo.key == userid).get()
    return modal.localPackages.render_template('settings.html', userid=userid, userinfo=userinfo)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)


