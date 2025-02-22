from flask import Flask, render_template, request, session, redirect
import requests
from urllib.parse import unquote
from flask_session import Session

from werkzeug.security import check_password_hash, generate_password_hash
#from curses.ascii  import (isalnum)

from helpers import login_required, database, split_dict, stringify,  readable_list
import os

app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
API_KEY = "YOUR_APIKEY"
@app.route("/")
@login_required
def index0():
    con, cur = database()
    name = cur.execute("SELECT name FROM users WHERE id = ?",(session["user_id"],)).fetchone()

    #name = name.fetchall()
    if name:
        name = name[0]  # Extract the name from the tuple
    else:
        name = "Guest"
    con.close()
    return render_template("index.html", name=name)

# Implement the fetch_random_recipes function
def fetch_random_recipes(number):
    url = f'https://api.spoonacular.com/recipes/random'
    params = {
        'apiKey': API_KEY,
        'number': 10,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['recipes']
    return []

@app.route('/home', methods=['GET'])
def home():
    #recipes = fetch_random_recipes(10)
    recipes = fetch_random_recipes(10)  # Fetch random recipes
    return render_template('index.html', recipes=recipes, search_query='')


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        query=request.form.get('search_query', '')
        recipes=search_recipes(query)
        return render_template('index.html', recipes=recipes, search_query=query, name=session.get("name", ""))
    search_query= request.args.get('search_query', '')
    decoded_search_query=unquote(search_query)
    recipes=search_recipes(decoded_search_query)
    return render_template('index.html', recipes=recipes, search_query=decoded_search_query, name=session.get("name", ""))

#func to search for recipes based on the provided query
def search_recipes(query):
    url = f'https://api.spoonacular.com/recipes/complexSearch'

    params = {
        'apiKey': API_KEY,
        'query':query,
        'number': 10,
        'instructionsRequired':True,
        'addRecipeInformation': True,
        'fillingIngredients':True,
        'maxReadyTime': 60,
        'addRecipeNutrition':True,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    return[]




@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    search_query = request.args.get('search_query', '')
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'apiKey': API_KEY,
    }

    response = requests.get(url, params = params)
    if response.status_code == 200:
        recipe = response.json()
        return render_template('view_recipe.html', recipe=recipe, search_query=search_query)
    return "Recipe not found", 404

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            message = "Please enter a valid username and/or password!"
            return render_template("login.html",
                                   message=message,
                                   )

        con, cur = database()
        rows = cur.execute("SELECT * FROM users WHERE username = ?",
                           (request.form.get("username"),)
                           )
        rows = rows.fetchall()

        validate_password = check_password_hash(rows[0][3], request.form.get("password"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not validate_password:
            message = "The username or password provided in the request are invalid!"
            return render_template("login.html",
                                   message=message,
                                   )

        session["user_id"] = rows[0][0]
        #session["name"] = rows[0][1]
        con.close()

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name").strip()
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not name or not username or not password:
            message = "Please enter a valid name and/or username and/or password!"
            return render_template("register.html",
                message=message,
            )
        if len(username) < 4 or not username.isalnum():
            message = "Username must contain al least one number, one letter, be between 0-9 character long"
            return render_template("register.html",
                message=message,
            )

        pw = generate_password_hash(password)

        try:
            con, cur = database()
            user = cur.execute("INSERT INTO users (name, username, hash) VALUES (?, ?, ?)",
                (name,
                username,
                pw)
            )
            con.commit()
            con.close()

            session["user_id"] = user.lastrowid

            return redirect("/")
        except:
            message = "Username has been taken. Please pick a different username!"
            return render_template("register.html",
                message=message,
            )

    else:
        return render_template("register.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)

