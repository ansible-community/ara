from flask import render_template, abort, Blueprint
from ara import models

play = Blueprint('play', __name__)


@play.route('/<play>/')
def show_play(play):
    play = models.Play.query.get(play)
    if play is None:
        abort(404)
    tasks = (models.Task.query
             .filter(models.Task.play_id == play.id)
             .order_by(models.Task.sortkey))

    return render_template('play.html',
                           play=play,
                           tasks=tasks)
