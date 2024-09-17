from flask import Flask
from app.models import db, Task
from app.schemas import TaskSchema
from app.resources import Tasks, FilterByStatus, TaskUpdation
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api

# Initialize the Flask app
app = Flask(__name__)

# Initialize the config (correcting the database URI config key)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To avoid warnings

# Uncomment and add a JWT secret key if needed
# app.config["JWT_SECRET_KEY"] = "your_secret_key_here"

# Initialize the extensions
db.init_app(app)
migrate = Migrate(app, db)
# jwt = JWTManager(app)  # Uncomment this line if you're using JWT

# Set up the API resources
api = Api(app)
api.add_resource(Tasks, "/tasks")
api.add_resource(TaskUpdation, "/tasks/<int:task_id>")
api.add_resource(FilterByStatus, "/tasks_by_status")

if __name__ == "__main__":
    app.run(debug=True)
