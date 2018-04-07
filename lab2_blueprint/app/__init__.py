from flask import Flask
app = Flask(__name__)
from app.module_1.view import mod
from app.module_2.view import mod
app.register_blueprint(module_1.view.mod)
app.register_blueprint(module_2.view.mod, url_prefix ='/mymodule2')