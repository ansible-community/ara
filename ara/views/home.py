from flask import render_template, Blueprint
from ara import models, utils

home = Blueprint('home', __name__)


@home.route('/')
def main():
    """ Returns the dashboard """
    playbooks = (models.Playbook.query
                 .order_by(models.Playbook.time_start.desc())
                 .limit(10))

    stats = utils.get_summary_stats(playbooks, 'playbook_id')

    return render_template('home.html', stats=stats)
