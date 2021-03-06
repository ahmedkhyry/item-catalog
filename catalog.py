from flask import (
                   Flask, render_template, request,
                   redirect, url_for, flash, jsonify)
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                   json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exist, if not make one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 300px; height: 300px;border-radius: 150px;
             -webkit-border-radius: 150px;-moz-border-radius: 150px;"> """
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(''''Current user
                   not connected.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = '''https://accounts.google.com/
          o/oauth2/revoke?token=%s''' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(''''Successfully
                   disconnected.'''), 200)
        response.headers['Content-Type'] = 'application/json'
        response = redirect("/", code=302)
        return response
    else:
        response = make_response(json.dumps('''Failed to
                   revoke token for given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Homepage displays all current categories with the latest added items.
@app.route('/')
def index():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.date)).limit(9)
    if 'username' not in login_session:
        return render_template('publicHome.html', categories=categories,
                               items=items)
    else:
        return render_template('home.html', categories=categories,
                               items=items)


# Selecting specific category shows you all the items for that category.
@app.route('/<categoryName>/items')
def showCategoryItem(categoryName):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=categoryName).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('showCategoryItems.html', categories=categories,
                           categoryName=categoryName, items=items)


# Selecting a specific item shows you specific information about that item.
@app.route('/catalog/<categoryName>/<itemName>')
def showItemDescription(categoryName, itemName):
    #   You will make 2 return .. 1 for public and other for private
    item = session.query(Item).filter_by(name=itemName).one()
    if 'username' not in login_session:
        return render_template('publicShowItemDescription.html', item=item)
    else:
        return render_template('showItemDescription.html', item=item)


# New Item
@app.route('/catalog/items/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       category=request.form['category'],
                       description=request.form['description'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newItem.html')


# Edit item
@app.route('/catalog/<itemName>/edit', methods=['GET', 'POST'])
def editItem(itemName):
    if 'username' not in login_session:
        return redirect('/login')
    edItem = session.query(Item).filter_by(name=itemName).one()
    if edItem.user_id != login_session['user_id'] and edItem.user_id != 1:
        return "You have to sign with ur email!"
    if request.method == 'POST':
        if request.form['name']:
            edItem.name = request.form['name']
        if request.form['description']:
            edItem.description = request.form['description']
        if request.form['category']:
            edItem.category = request.form['category']
        edItem.user_id = login_session['user_id']
        session.add(edItem)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('editItem.html', item=edItem)


# Delete Item
@app.route('/catalog/<itemName>/delete', methods=['GET', 'POST'])
def deleteItem(itemName):
    if 'username' not in login_session:
        return redirect('/login')
    delItem = session.query(Item).filter_by(name=itemName).one()
    if delItem.user_id != login_session['user_id'] and delItem.user_id != 1:
        return "You have to sign with ur email!"
    if request.method == 'POST':
        session.delete(delItem)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('deleteItem.html', item=delItem)


@app.route('/catalog.json')
def api():
    catalogs = session.query(Category).all()
    result = []
    for cat in catalogs:
        items = session.query(Item).filter_by(category_id=cat.id).all()
        serialize_cat = cat.serialize
        serialize_cat['items'] = [i.serialize for i in items]
        result.append(serialize_cat)
    return jsonify(Category=result)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
