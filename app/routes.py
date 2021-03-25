from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, NewForm
from app.models import Users, Reviews, Access
from datetime import datetime
from sqlalchemy import desc
import json
from dotenv import load_dotenv
import requests
import os


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        try:
            if current_user.is_authenticated:
                track = Access(user_id=current_user.id, ip=request.headers['X-Real-IP'], time=datetime.utcnow(), path=request.full_path)
                db.session.add(track)
                db.session.commit()
            else:
                track = Access(user_id=0, ip=request.headers['X-Real-IP'], time=datetime.utcnow(), path=request.full_path)
                db.session.add(track)
                db.session.commit()
        except:
            pass

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Denver Breakfast Burrito Ratings')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data.lower(), email=form.email.data, phone=form.phone.data, first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = Users.query.filter_by(username=username).first_or_404()
    
    return render_template('user.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    restaurants = Reviews.query.order_by(Reviews.restaurant_name.asc()).all()
    return render_template('reviews.html', title="Denver Breakfast Burrito Reviews", restaurants=restaurants)

@app.route('/reviews/<restaurant_name>', methods=['GET', 'POST'])
def restaurant(restaurant_name):
    restaurant = Reviews.query.filter_by(restaurant_name=restaurant_name).limit(1).first_or_404()
    return render_template('restaurant.html', title=f"{restaurant_name} Breakfast Burrito", restaurant=restaurant)

@app.route('/admin/new', methods=['GET', 'POST'])
def admin_new():
    form = NewForm()
    if form.validate_on_submit():
        g_address = form.address.data.replace(" ", "+")
        g_city = form.city.data.replace(" ", "+")
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={g_address},+{g_city},+{form.state.data}&key={os.environ.get('API')}"
        r = requests.get(url)
        j = json.loads(r.text)
        latitude = j['results'][0]['geometry']['location']['lat']
        longitude = j['results'][0]['geometry']['location']['lng']
        overall_score = form.tortilla_score.data * 2.0 + form.potato_score.data * 2 + form.texture_score.data * 2 + form.flavor_score.data * 2 + form.general_score.data * 2
        overall_score = int(overall_score)
        burrito = Reviews(overview=form.overview.data, user_id=current_user.id, overall_score=overall_score, lat=latitude, lng=longitude, date=form.date.data, restaurant_name=form.restaurant_name.data, address=form.address.data, city=form.city.data, state=form.state.data, zip_code=form.zip_code.data, tortilla_desc=form.tortilla_desc.data, tortilla_score=form.tortilla_score.data, potato_desc=form.potato_desc.data, potato_score=form.potato_score.data, texture_desc=form.texture_desc.data, texture_score=form.texture_score.data, flavor_desc=form.flavor_desc.data, flavor_score=form.flavor_score.data, general_desc=form.general_desc.data, general_score=form.general_score.data, smother=form.smother.data, smother_score=form.smother_score.data, published=form.published.data)
        db.session.add(burrito)
        db.session.commit()
        flash(f'Your post is now live!')
        return redirect(url_for('index'))
    return render_template('new_burrito.html', title='New Burrito', form=form)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route('/map', methods=['GET', 'POST'])
@login_required
def map():
    latlong = Station.query.from_statement(db.text("SELECT *  FROM station WHERE country = 'US' AND taf = TRUE;")).all()
    MTN_OBSCN = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'MTN OBSCN';"))
    IFR = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'IFR';"))
    TURB = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'TURB';"))
    ICE = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'ICE';"))
    pireps = Pirep.query.from_statement(db.text("SELECT * FROM pirep WHERE observation_time >= NOW() - INTERVAL '1 HOUR';")).all()
    CONVECTIVE = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'CONVECTIVE';"))
    ASH = Airsigmet.query.from_statement(db.text("SELECT * FROM airsigmet WHERE valid_time_to >= NOW() AND hazard = 'ASH';"))
    try:
        url = f"http://api.ipstack.com/{request.headers['X-Real-IP']}?access_key={os.environ.get('IPSTACK')}"
        r = requests.get(url)
        j = json.loads(r.text)
        latitude = j['latitude']
        longitude = j['longitude']
    except:
        latitude = 44.967243
        longitude = -103.771556
    return render_template('map.html', title='Follow', latlong=latlong, MTN_OBSCN=MTN_OBSCN, pireps=pireps, IFR=IFR, TURB=TURB, ICE=ICE, CONVECTIVE=CONVECTIVE, ASH=ASH, latitude=latitude, longitude=longitude)