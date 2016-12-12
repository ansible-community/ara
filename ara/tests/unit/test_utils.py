import ara.utils as u
import json

from common import TestAra


class TestUtils(TestAra):
    '''Tests the utils module'''
    def setUp(self):
        super(TestUtils, self).setUp()
        self.env = self.app.jinja_env

    def tearDown(self):
        super(TestUtils, self).tearDown()

    def test_status_to_query(self):
        res = u.status_to_query('ok')
        self.assertEqual(res, {'status': 'ok'})

    def test_status_to_query_changed(self):
        res = u.status_to_query('changed')
        self.assertEqual(res, {'status': 'ok', 'changed': True})

    def test_format_json(self):
        data = json.dumps({'name': 'value'})
        res = u.format_json(json.dumps(data))
        self.assertEqual(res, '"{\\"name\\": \\"value\\"}"')

    def test_format_json_fail(self):
        res = u.format_json('{invalid:}')
        self.assertEqual(res, '{invalid:}')
