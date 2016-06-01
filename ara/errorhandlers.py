from flask import render_template


def configure_errorhandlers(app):

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', error=error), 404
