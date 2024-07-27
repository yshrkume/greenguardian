from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from app import app, db, login_manager
from app.forms import SignupForm, LoginForm, PlantForm
from app.models import User, Plant
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse


@app.route("/")
def home():
    if current_user.is_authenticated:
        plants = Plant.query.filter_by(owner_id=current_user.id).limit(5).all()
        upcoming_watering_plants = [
            plant
            for plant in plants
            if plant.next_watering_date()
            and 0 <= (plant.next_watering_date() - datetime.utcnow().date()).days <= 7
        ]
        return render_template(
            "home.html",
            plants=plants,
            upcoming_watering_plants=upcoming_watering_plants,
            user=current_user,
        )
    else:
        return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password")
            return redirect(url_for("login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/plants", methods=["GET", "POST"])
@login_required
def list_plants():
    plants = Plant.query.filter_by(owner_id=current_user.id).all()
    return render_template("plants_list.html", plants=plants)


@app.route("/plant/<int:plant_id>")
@login_required
def plant_detail(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if plant.owner_id != current_user.id:
        flash("You do not have permission to view this plant.")
        return redirect(url_for("list_plants"))
    return render_template("plant_detail.html", plant=plant)


@app.route("/add_plant", methods=["GET", "POST"])
@login_required
def add_plant():
    form = PlantForm()
    if form.validate_on_submit():
        plant = Plant(
            name=form.name.data,
            purchase_date=form.purchase_date.data,
            light_conditions=form.light_conditions.data,
            watering_frequency=form.watering_frequency.data,
            fertilizing_frequency=form.fertilizing_frequency.data,
            notes=form.notes.data,
            owner=current_user,
        )
        db.session.add(plant)
        db.session.commit()
        flash("Plant has been added successfully.")
        return redirect(url_for("list_plants"))
    return render_template("add_plant.html", form=form)


@app.route("/notifications")
@login_required
def notifications():
    if current_user.is_authenticated:
        plants = Plant.query.filter_by(owner_id=current_user.id).all()
        upcoming_watering_plants = [
            plant
            for plant in plants
            if plant.next_watering_date()
            and 0 <= (plant.next_watering_date() - datetime.utcnow().date()).days <= 7
        ]
        return render_template(
            "notifications.html", upcoming_watering_plants=upcoming_watering_plants
        )
    else:
        flash("You need to be logged in to access this page.")
        return redirect(url_for("login"))
