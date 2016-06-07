from flask.ext.testing import TestCase
import ara.webapp as w
import ara.models as m
import ara.utils as u
import json

from mock import Mock


class TestUtils(TestCase):
    '''Tests the utils module'''

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return w.create_app(self)

    def setUp(self):
        m.db.create_all()
        self.env = self.app.jinja_env

    def tearDown(self):
        m.db.session.remove()
        m.db.drop_all()

    def test_status_to_query(self):
        res = u.status_to_query('ok')
        self.assertEqual(res, {'status': 'ok'})

    def test_status_to_query_changed(self):
        res = u.status_to_query('changed')
        self.assertEqual(res, {'status': 'ok', 'changed': True})

    def test_format_json(self):
        data = json.dumps({'name': 'value'})
        res = u.format_json(json.dumps(data))
        self.assertEqual(res,
                         '"{\\"name\\": \\"value\\"}"')

    def test_format_json_fail(self):
        res = u.format_json('{invalid:}')
        self.assertEqual(res, '{invalid:}')
