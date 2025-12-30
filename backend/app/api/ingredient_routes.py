from flask import Blueprint, jsonify
from app.models import *

ingredient_bp = Blueprint('ingredient', __name__, url_prefix='/ingredient')

@ingredient_bp.route('/', methods=['GET'])
def get_all_ingredients():
    ingredients = Ingredient.query.all()
    return jsonify([{
        "id": i.id,
        "name": i.name,
        "des": i.desc,
        "unit": i.measurement_unit
    } for i in ingredients]), 200