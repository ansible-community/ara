import datetime
import json
import logging
import os


def configure_template_filters(app):
    log = logging.getLogger('%s.filters' % app.logger_name)

    @app.template_filter('datefmt')
    def jinja_date_formatter(timestamp, format='%Y-%m-%d %H:%M:%S'):
        """ Reformats a datetime timestamp from str(datetime.datetime)"""
        return datetime.datetime.strftime(timestamp, format)

    @app.template_filter('timefmt')
    def jinja_time_formatter(timestamp):
        """ Reformats a datetime timedelta """
        d = datetime.timedelta(seconds=int(timestamp.total_seconds()))
        return str(d)

    @app.template_filter('to_nice_json')
    def jinja_to_nice_json(result):
        """ Formats a result """
        return json.dumps(result, indent=4, sort_keys=True,
                          default=str)

    @app.template_filter('from_json')
    def jinja_from_json(val):
        try:
            return json.loads(val)
        except Exception as err:
            log.error('failed to load json: %s', err)
            return val

    @app.template_filter('pathtruncate')
    def jinja_pathtruncate(path):
        '''Truncates a path to less than ARA_PATH_MAX characters.  Paths
        are truncated on path separators.  We prepend an ellipsis when we
        return a truncated path.'''

        if path is None:
            return

        if len(path) < app.config['ARA_PATH_MAX']:
            return path

        # always include the basename
        head, tail = os.path.split(path)
        newpath = tail

        while tail:
            if len(newpath) + len(tail) > app.config['ARA_PATH_MAX']:
                break
            newpath = os.path.join(tail, newpath)
            head, tail = os.path.split(head)

        prefix = '...' if len(newpath) < len(path) else ''
        return os.path.join(prefix, newpath)
