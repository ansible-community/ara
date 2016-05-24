from flask import render_template, Blueprint

home = Blueprint('home', __name__)


@home.route('/')
def main():
    """ Returns the home page """
    return render_template('home.html')
