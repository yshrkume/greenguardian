import requests
from datetime import datetime, timedelta
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    make_response,
)
from app import app
from app.forms import SignupForm, LoginForm, PlantForm, UpdateAccountForm
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)

AUTH_SERVICE_URL = "http://auth_service:5000"
PLANT_SERVICE_URL = "http://plant_service:5000"
NOTIFICATION_SERVICE_URL = "http://notification_service:5000"
STATISTICS_SERVICE_URL = "http://statistics_service:5000"
GREETING_SERVICE_URL = "http://greeting_service:5000"


@app.route("/")
@jwt_required(optional=True, locations=["cookies"])
def home():
    user = get_jwt_identity()
    if user:
        response = requests.get(
            f"{PLANT_SERVICE_URL}/plants", params={"user_id": user["id"]}
        )
        if response.status_code == 200:
            plants = response.json()
        else:
            plants = []

        start_date = datetime.utcnow().strftime("%Y-%m-%d")
        end_date = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")

        watering_response = requests.post(
            f"{NOTIFICATION_SERVICE_URL}/watering_notifications?start_date={start_date}&end_date={end_date}",
            json={"plants": plants},
        )
        fertilizing_response = requests.post(
            f"{NOTIFICATION_SERVICE_URL}/fertilizing_notifications?start_date={start_date}&end_date={end_date}",
            json={"plants": plants},
        )
        watering_notifications = watering_response.json().get(
            "upcoming_watering_plants", []
        )
        fertilizing_notifications = fertilizing_response.json().get(
            "upcoming_fertilizing_plants", []
        )

        statistics_payload = {"plants": plants}
        freq_counts = requests.post(
            f"{STATISTICS_SERVICE_URL}/watering_frequency_count",
            json=statistics_payload,
        ).json()

        tasks_response = requests.post(
            f"{STATISTICS_SERVICE_URL}/upcoming_tasks_count",
            json={"plants": plants},
        )
        if tasks_response.status_code == 200:
            tasks_data = tasks_response.json()
            upcoming_watering_tasks = tasks_data.get("upcoming_watering_tasks", 0)
            upcoming_fertilizing_tasks = tasks_data.get("upcoming_fertilizing_tasks", 0)
        else:
            upcoming_watering_tasks = 0
            upcoming_fertilizing_tasks = 0

        greeting_response = requests.get(f"{GREETING_SERVICE_URL}/greetAPI")
        greeting = greeting_response.json().get("greeting", "")
        return render_template(
            "home.html",
            plants=plants,
            upcoming_watering_plants=watering_notifications,
            upcoming_fertilizing_plants=fertilizing_notifications,
            freq_counts=freq_counts,
            upcoming_watering_tasks=upcoming_watering_tasks,
            upcoming_fertilizing_tasks=upcoming_fertilizing_tasks,
            greeting=greeting,
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
    query = request.args.get("query", "")
    params = {"user_id": user["id"]}
    if query:
        params["name"] = query

    response = requests.get(f"{PLANT_SERVICE_URL}/plants", params=params)
    if response.status_code == 200:
        plants = response.json()
    else:
        plants = []

    return render_template("plants_list.html", plants=plants, query=query)


@app.route("/plant/<int:plant_id>")
@jwt_required(locations=["cookies"])
def plant_detail(plant_id):
    user_id = get_jwt_identity()["id"]
    response = requests.get(
        f"{PLANT_SERVICE_URL}/plants/{plant_id}", params={"user_id": user_id}
    )
    if response.status_code == 200:
        plant = response.json()
        return render_template("plant_detail.html", plant=plant)
    else:
        flash("Failed to load plant details")
        return redirect(url_for("list_plants"))


@app.route("/add_plant", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def add_plant():
    user_id = get_jwt_identity()["id"]
    form = PlantForm()
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "purchase_date": form.purchase_date.data.isoformat(),
            "light_conditions": form.light_conditions.data,
            "watering_frequency": form.watering_frequency.data,
            "fertilizing_frequency": form.fertilizing_frequency.data,
            "notes": form.notes.data,
            "user_id": user_id,
        }
        response = requests.post(f"{PLANT_SERVICE_URL}/plants", json=data)
        if response.status_code == 201:
            flash("Plant has been added successfully.")
            return redirect(url_for("list_plants"))
        else:
            flash("Failed to add plant")
    return render_template("add_plant.html", form=form)


@app.route("/edit_plant/<int:plant_id>", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
def edit_plant(plant_id):
    user = get_jwt_identity()
    response = requests.get(
        f"{PLANT_SERVICE_URL}/plants/{plant_id}", params={"user_id": user["id"]}
    )

    if response.status_code != 200:
        flash("Error fetching plant details")
        return redirect(url_for("list_plants"))

    plant_data = response.json()
    plant_data["purchase_date"] = datetime.strptime(
        plant_data["purchase_date"], "%Y-%m-%d"
    )
    form = PlantForm(data=plant_data)

    if form.validate_on_submit():
        update_response = requests.put(
            f"{PLANT_SERVICE_URL}/plants/{plant_id}",
            json={
                "name": form.name.data,
                "purchase_date": form.purchase_date.data.strftime("%Y-%m-%d"),
                "light_conditions": form.light_conditions.data,
                "watering_frequency": form.watering_frequency.data,
                "fertilizing_frequency": form.fertilizing_frequency.data,
                "notes": form.notes.data,
                "user_id": user["id"],
            },
        )

        if update_response.status_code == 200:
            flash("Plant updated successfully.")
            return redirect(url_for("list_plants"))
        else:
            flash("Error updating plant.")

    return render_template("edit_plant.html", form=form, plant_id=plant_id)


@app.route("/delete_plant/<int:plant_id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def delete_plant(plant_id):
    user_id = get_jwt_identity()["id"]
    response = requests.delete(
        f"{PLANT_SERVICE_URL}/plants/{plant_id}", params={"user_id": user_id}
    )
    if response.status_code == 200:
        flash("Plant has been deleted successfully.")
    else:
        flash("Failed to delete plant")
    return redirect(url_for("list_plants"))


@app.route("/notifications")
@jwt_required(locations=["cookies"])
def notifications():
    user = get_jwt_identity()
    if user:
        response = requests.get(f"{PLANT_SERVICE_URL}/plants?user_id={user['id']}")
        plants = response.json()

        start_date = datetime.utcnow().strftime("%Y-%m-%d")
        end_date = (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d")

        watering_response = requests.post(
            f"{NOTIFICATION_SERVICE_URL}/watering_notifications?start_date={start_date}&end_date={end_date}",
            json={"plants": plants},
        )
        fertilizing_response = requests.post(
            f"{NOTIFICATION_SERVICE_URL}/fertilizing_notifications?start_date={start_date}&end_date={end_date}",
            json={"plants": plants},
        )

        watering_notifications = watering_response.json().get(
            "upcoming_watering_plants", []
        )
        fertilizing_notifications = fertilizing_response.json().get(
            "upcoming_fertilizing_plants", []
        )

        return render_template(
            "notifications.html",
            watering_notifications=watering_notifications,
            fertilizing_notifications=fertilizing_notifications,
            user=user,
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
