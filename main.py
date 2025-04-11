import os
import binascii
from datetime import timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask_restful import Resource, Api, reqparse
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask import Flask, jsonify, request, render_template
from src.database.base import db
from src.database import db_actions

load_dotenv()

app = Flask(__name__)
CORS(app)

# Конфигурации
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_URI")
app.config["JWT_SECRET_KEY"] = binascii.hexlify(os.urandom(24)).decode()
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

# Инициализация компонентов
db.init_app(app)
api = Api(app)
migrate = Migrate(app, db)
jwt_manager = JWTManager(app)

# Глобальная обработка ошибок
@app.route("/product/<product_id>/", methods=["GET"])
def get_product_page(product_id):
    """Маршрут для отображения страницы продукта"""
    try:
        product = db_actions.get_product(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product), 200  # Или рендеринг HTML-страницы, если нужно
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/debug/products", methods=["GET"])
def debug_products():
    """Маршрут для отладки: проверка данных продуктов"""
    try:
        products = db_actions.get_products()
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/", methods=["GET"])
def index():
    """Главная страница с продуктами"""
    try:
        products = db_actions.get_products()
        if not products:
            products = []  # Если продуктов нет, передаём пустой список
        return render_template("index.html", products=products)
    except Exception as e:
        return render_template("index.html", products=[], error=str(e))
    



@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500


class ProductAPI(Resource):
    def get(self, prod_id=None):
        """Получить все продукты или один продукт по ID"""
        try:
            if prod_id:
                product = db_actions.get_product(prod_id)
                if not product:
                    return jsonify({"error": "Product not found"}), 404
                return jsonify(product), 200

            products = db_actions.get_products()
            if not products:
                return jsonify({"error": "No products found"}), 404
            return jsonify(products), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def post(self):
        """Добавить новый продукт"""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("name", required=True, help="Name is required")
            parser.add_argument("description")
            parser.add_argument("img_url")
            parser.add_argument("price", type=float, required=True, help="Price is required")
            kwargs = parser.parse_args()
            prod_id = db_actions.add_product(**kwargs)
            return jsonify({"message": f"Product successfully added with id '{prod_id}'"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def put(self, prod_id):
        """Обновить продукт по ID"""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("name")
            parser.add_argument("description")
            parser.add_argument("img_url")
            parser.add_argument("price", type=float)
            kwargs = parser.parse_args()
            updated = db_actions.update_product(prod_id=prod_id, **kwargs)
            if not updated:
                return jsonify({"error": "Product not found"}), 404
            return jsonify({"message": "Product successfully updated"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def delete(self, prod_id):
        """Удалить продукт по ID"""
        try:
            deleted = db_actions.del_product(prod_id)
            if not deleted:
                return jsonify({"error": "Product not found"}), 404
            return jsonify({"message": "Product successfully deleted"}), 204
        except Exception as e:
            return jsonify({"error": str(e)}), 500


class UserAPI(Resource):
    @jwt_required()
    def get(self):
        """Получить данные пользователя по JWT"""
        try:
            user_id = get_jwt_identity()
            user = db_actions.get_user(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            del user["_password"]
            return jsonify(user), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def post(self):
        """Создать нового пользователя"""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("first_name", required=True, help="First name is required")
            parser.add_argument("last_name", required=True, help="Last name is required")
            parser.add_argument("email", required=True, help="Email is required")
            parser.add_argument("password", required=True, help="Password is required")
            kwargs = parser.parse_args()
            msg = db_actions.add_user(**kwargs)
            return jsonify({"message": msg}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


class TokenAPI(Resource):
    @jwt_required(refresh=True)
    def get(self):
        """Получить новый токен по refresh токену"""
        try:
            user_id = get_jwt_identity()
            token = {"access_token": create_access_token(identity=user_id)}
            return jsonify(token), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def post(self):
        """Получить токены по email и паролю"""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("email", required=True, help="Email is required")
            parser.add_argument("password", required=True, help="Password is required")
            kwargs = parser.parse_args()
            tokens = db_actions.get_tokens(**kwargs)
            if not tokens:
                return jsonify({"error": "Invalid credentials"}), 401
            return jsonify(tokens), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Регистрация всех API ресурсов
api.add_resource(ProductAPI, "/api/products/", "/api/products/<prod_id>/")
api.add_resource(UserAPI, "/api/users/")
api.add_resource(TokenAPI, "/api/tokens/")

# Приветственное сообщение в консоли
print(f"SQLALCHEMY_DATABASE_URI: {os.getenv('SQLALCHEMY_URI')}")

if __name__ == "__main__":
    app.run(debug=True, port=3000)