import datetime
import json
import logging
import os


def configure_template_filters(app):
    log = logging.getLogger('%s.filters' % app.logger_name)

    @app.template_filter('datefmt')
    def jinja_date_formatter(timestamp, format='%Y-%m-%d %H:%M:%S'):
        """ Reformats a datetime timestamp from str(datetime.datetime)"""
        if timestamp is None:
            return 'n/a'
        else:
            return datetime.datetime.strftime(timestamp, format)

    @app.template_filter('timefmt')
    def jinja_time_formatter(timestamp):
        """ Reformats a datetime timedelta """
        if timestamp is None:
            return 'n/a'
        else:
            d = datetime.timedelta(seconds=int(timestamp.total_seconds()))
            return str(d)

    @app.template_filter('to_nice_json')
    def jinja_to_nice_json(result):
        """ Tries to format a result as a pretty printed JSON. """
        try:
            return json.dumps(json.loads(result), indent=4, sort_keys=True)
        except (ValueError, TypeError):
            try:
                return json.dumps(result, indent=4, sort_keys=True)
            except TypeError as err:
                log.error('failed to dump json: %s', err)
                return result

    @app.template_filter('from_json')
    def jinja_from_json(val):
        try:
            return json.loads(val)
        except ValueError as err:
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

        dirname, basename = os.path.split(path)
        while dirname:
            if len(dirname) + len(basename) < app.config['ARA_PATH_MAX']:
                break
            dirlist = dirname.split('/')
            dirlist.pop(0)
            dirname = "/".join(dirlist)

        return "..." + os.path.join(dirname, basename)
