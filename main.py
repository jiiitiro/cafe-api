from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import random

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)
api_key = "TopSecretAPIKey"


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    random_cafe_dict = {
        'cafe': {
            'can_take_calls': random_cafe.can_take_calls,
            'coffee_price': random_cafe.coffee_price,
            'has_sockets': random_cafe.has_sockets,
            'has_toilet': random_cafe.has_toilet,
            'has_wifi': random_cafe.has_wifi,
            'id': random_cafe.id,
            'img_url': random_cafe.img_url,
            'location': random_cafe.location,
            'map_url': random_cafe.map_url,
            'name': random_cafe.name,
            'seats': random_cafe.seats
        }
    }
    response = jsonify(random_cafe_dict)
    return response


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    cafes_dict = [
        {
            'can_take_calls': cafe.can_take_calls,
            'coffee_price': cafe.coffee_price,
            'has_sockets': cafe.has_sockets,
            'has_toilet': cafe.has_toilet,
            'has_wifi': cafe.has_wifi,
            'id': cafe.id,
            'img_url': cafe.img_url,
            'location': cafe.location,
            'map_url': cafe.map_url,
            'name': cafe.name,
            'seats': cafe.seats
        } for cafe in cafes]

    response = jsonify({'cafes': cafes_dict})
    return response


@app.route("/search")
def cafe_location():
    query_location = request.args.get("loc").title()
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    cafes = result.scalars().all()
    if not cafes:
        error = {
            'error': {
                'Not Found': "Sorry, we don't have cafe at that location."
            }
        }
        response = jsonify(error)
    else:
        all_cafes_dict = [
            {
                'can_take_calls': cafe.can_take_calls,
                'coffee_price': cafe.coffee_price,
                'has_sockets': cafe.has_sockets,
                'has_toilet': cafe.has_toilet,
                'has_wifi': cafe.has_wifi,
                'id': cafe.id,
                'img_url': cafe.img_url,
                'location': cafe.location,
                'map_url': cafe.map_url,
                'name': cafe.name,
                'seats': cafe.seats
            } for cafe in cafes]

        response = jsonify({'cafes': all_cafes_dict})
    return response


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    try:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"Success": "Successfully added the new cafe."})
    except Exception as e:
        db.session.rollback()
        return jsonify(error={"Message": f"Failed to add the new cafe. Error: {str(e)}"}), 500


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = db.session.get(Cafe, cafe_id)
    if not cafe_to_update:
        return jsonify(error={"Error": {"Not Found": "Sorry a cafe with that id was not found in the database."}})
    else:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated the price."})


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key_params = request.args.get("api-key")
    if api_key_params == api_key:
        cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success={"Success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True, port=50010)
