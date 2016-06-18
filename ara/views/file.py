from flask import render_template, abort, Blueprint
from ara import models

file = Blueprint('file', __name__)


@file.route('/<file_>/')
def show_file(file_):
    """ Returns details of a file """
    file_ = (models.File.query.get(file_))
    if file_ is None:
        abort(404)

    return render_template('file.html', file_=file_)
