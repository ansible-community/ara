import json

from flask import render_template, abort, Blueprint
from ara import models

host = Blueprint('host', __name__)


@host.route('/<id>/')
def show_host(id):
    try:
        host = models.Host.query.get(id)
    except models.NoResultFound:
        abort(404)

    if host and host.facts:
        facts = sorted(json.loads(host.facts.values).iteritems())
    else:
        abort(404)

    return render_template('host.html',
                           host=host,
                           facts=facts)
