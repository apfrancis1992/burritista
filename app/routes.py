from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, NewForm, ContactForm, EditForm
from app.models import Users, Reviews, Access
from datetime import datetime
from sqlalchemy import desc
from functools import wraps
import json
from dotenv import load_dotenv
import requests
import os


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_anonymous:  
            return redirect('https://www.youtube.com/watch/dQw4w9WgXcQ')
        elif current_user.access == 1:
            return f(*args, **kwargs)
        else:
            return redirect('https://www.youtube.com/watch/dQw4w9WgXcQ')
    return wrap

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


@app.route('/how_we_rate', methods=['GET', 'POST'])
def how_we_rate():
    return render_template('how_we_rate.html', title='Denver Breakfast Burrito Ratings')


@app.route('/burrito_banter', methods=['GET', 'POST'])
def burrito_banter():
    return render_template('burrito_banter.html', title='Denver Breakfast Burrito Ratings')


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
    restaurants = Reviews.query.order_by(Reviews.overall_score.desc()).filter_by(published='Yes')
    return render_template('reviews.html', title="Denver Breakfast Burrito Reviews", restaurants=restaurants)

@app.route('/reviews/<restaurant_name>', methods=['GET', 'POST'])
def restaurant(restaurant_name):
    restaurant = Reviews.query.filter_by(restaurant_name=restaurant_name).limit(1).first_or_404()
    return render_template('restaurant.html', title=f"{restaurant_name} Breakfast Burrito", restaurant=restaurant)

@app.route('/admin/new', methods=['GET', 'POST'])
@admin_required
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

@app.route('/admin/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit():
    reviews = Reviews.query.order_by(Reviews.restaurant_name.asc()).all()
    return render_template('reviews_admin.html', title='Admin Reviews',
                           reviews=reviews)

@app.route('/admin/edit/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_post(id):
    review = Reviews.query.filter_by(id=id).first_or_404()
    form = EditForm()
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
        review.overview=form.overview.data
        review.user_id=current_user.id
        review.overall_score=overall_score
        review.lat=latitude
        review.lng=longitude
        review.date=form.date.data
        review.restaurant_name=form.restaurant_name.data
        review.address=form.address.data
        review.city=form.city.data
        review.state=form.state.data
        review.zip_code=form.zip_code.data
        review.tortilla_desc=form.tortilla_desc.data
        review.tortilla_score=form.tortilla_score.data
        review.potato_desc=form.potato_desc.data
        review.potato_score=form.potato_score.data
        review.texture_desc=form.texture_desc.data
        review.texture_score=form.texture_score.data
        review.flavor_desc=form.flavor_desc.data
        review.flavor_score=form.flavor_score.data
        review.general_desc=form.general_desc.data
        review.general_score=form.general_score.data
        review.smother=form.smother.data
        review.smother_score=form.smother_score.data
        review.published=form.published.data
        db.session.commit()
        return redirect(url_for('admin_edit'))
    elif request.method == 'GET':
        form.overview.data=review.overview
        form.date.data=review.date
        form.restaurant_name.data=review.restaurant_name
        form.address.data=review.address
        form.city.data=review.city
        form.state.data=review.state
        form.zip_code.data=review.zip_code
        form.tortilla_desc.data=review.tortilla_desc
        form.tortilla_score.data=review.tortilla_score
        form.potato_desc.data=review.potato_desc
        form.potato_score.data=review.potato_score
        form.texture_desc.data=review.texture_desc
        form.texture_score.data=review.texture_score
        form.flavor_desc.data=review.flavor_desc
        form.flavor_score.data=review.flavor_score
        form.general_desc.data=review.general_desc
        form.general_score.data=review.general_score
        form.smother.data=review.smother
        form.smother_score.data=review.smother_score
        form.published.data=review.published
    return render_template('admin_edit_post.html', title='Edit Burrito', form=form)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')
