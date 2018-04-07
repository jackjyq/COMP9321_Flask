from flask import Blueprint, render_template
mod = Blueprint('module_1', __name__)
@mod.route('/homepage')
def homepage():
    return render_template("students.html", students=[1])