import requests
from datetime import datetime
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    make_response,
)
from app import app, db
from app.forms import SignupForm, LoginForm, PlantForm, UpdateAccountForm
from app.models import Plant
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)

AUTH_SERVICE_URL = "http://auth_service:5000"


@app.route("/")
@jwt_required(optional=True, locations=["cookies"])
def home():
    user = get_jwt_identity()
    if user:
        plants = Plant.query.filter_by(owner_id=user["id"]).limit(5).all()
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
            user=user,
        )
    else:
        return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        response = requests.post(
            f"{AUTH_SERVICE_URL}/register",
            json={
                "username": form.username.data,
                "email": form.email.data,
                "password": form.password.data,
            },
        )
        if response.status_code == 201:
            flash("Congratulations, you are now a registered user!")
            return redirect(url_for("login"))
        else:
            flash("Error registering user.")
            return redirect(url_for("signup"))
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        response = requests.post(
            f"{AUTH_SERVICE_URL}/login",
            json={"username": form.username.data, "password": form.password.data},
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            resp = make_response(redirect(url_for("home")))
            set_access_cookies(resp, token)
            return resp
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("home")))
    unset_jwt_cookies(resp)
    flash("Logout successful")
    return resp


@app.route("/plants", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def list_plants():
    user = get_jwt_identity()
    query = request.args.get("query")
    if query:
        plants = Plant.query.filter(
            Plant.owner_id == user["id"], Plant.name.ilike(f"%{query}%")
        ).all()
    else:
        plants = Plant.query.filter_by(owner_id=user["id"]).all()
    return render_template("plants_list.html", plants=plants, query=query)


@app.route("/plant/<int:plant_id>")
@jwt_required(locations=["cookies"])
def plant_detail(plant_id):
    user = get_jwt_identity()
    plant = Plant.query.get_or_404(plant_id)
    if plant.owner_id != user["id"]:
        flash("You do not have permission to view this plant.")
        return redirect(url_for("list_plants"))
    return render_template("plant_detail.html", plant=plant)


@app.route("/add_plant", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def add_plant():
    user = get_jwt_identity()
    form = PlantForm()
    if form.validate_on_submit():
        plant = Plant(
            name=form.name.data,
            purchase_date=form.purchase_date.data,
            light_conditions=form.light_conditions.data,
            watering_frequency=form.watering_frequency.data,
            fertilizing_frequency=form.fertilizing_frequency.data,
            notes=form.notes.data,
            owner_id=user["id"],
        )
        db.session.add(plant)
        db.session.commit()
        flash("Plant has been added successfully.")
        return redirect(url_for("list_plants"))
    return render_template("add_plant.html", form=form)


@app.route("/delete_plant/<int:plant_id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def delete_plant(plant_id):
    user = get_jwt_identity()
    plant = Plant.query.get_or_404(plant_id)
    if plant.owner_id != user["id"]:
        flash("You do not have permission to delete this plant.")
        return redirect(url_for("list_plants"))
    db.session.delete(plant)
    db.session.commit()
    flash("Plant has been deleted successfully.")
    return redirect(url_for("list_plants"))


@app.route("/notifications")
@jwt_required(locations=["cookies"])
def notifications():
    user = get_jwt_identity()
    if user:
        plants = Plant.query.filter_by(owner_id=user["id"]).all()
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


@app.route("/account", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def account():
    response = requests.get(
        f"{AUTH_SERVICE_URL}/profile",
        headers={
            "Authorization": f'Bearer {request.cookies.get("access_token_cookie")}'
        },
    )
    if response.status_code == 200:
        user_data = response.json()
        form = UpdateAccountForm()
        if form.validate_on_submit():
            update_response = requests.put(
                f"{AUTH_SERVICE_URL}/update",
                headers={
                    "Authorization": f'Bearer {request.cookies.get("access_token_cookie")}',
                },
                json={
                    "username": form.username.data,
                    "email": form.email.data,
                    "password": form.password.data,
                    "current_password": form.current_password.data,
                },
            )
            if update_response.status_code == 200:
                flash("Your account has been updated.")
                return redirect(url_for("account"))
            else:
                flash("Failed to update account.")
        elif request.method == "GET":
            form.username.data = user_data["username"]
            form.email.data = user_data["email"]
        return render_template("account.html", form=form)
    else:
        flash("Error fetching user profile")
        return redirect(url_for("home"))
