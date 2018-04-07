from flask import Blueprint
mod = Blueprint('module_2', __name__)
@mod.route('/getstuff')
def getstuff():
    return '{"value":"You are in the module_2"}'