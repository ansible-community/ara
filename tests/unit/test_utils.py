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

    def test_fields_from_iter(self):
        fields = (
            ('Field 1',),
            ('Field 2', 'field2'),
            ('Field 3', 'field3.value'),
        )

        items = [
            Mock(field_1='value 1', field2='value 2',
                 field3=Mock(value='value 3')),
        ]

        res = u.fields_from_iter(fields, items)

        self.assertEqual(res,
                         (('Field 1', 'Field 2', 'Field 3'),
                          [['value 1', 'value 2', 'value 3']]))

    def test_fields_from_iter_xform(self):
        fields = (
            ('Field 1',),
            ('Field 2', 'field2'),
        )

        items = [
            Mock(field_1='value 1', field2='value 2'),
        ]

        res = u.fields_from_iter(fields, items,
                                 xforms={'Field 2': lambda x: x.upper()})

        self.assertEqual(res,
                         (('Field 1', 'Field 2'), [['value 1', 'VALUE 2']]))

    def test_fields_from_object(self):
        fields = (
            ('Field 1',),
            ('Field 2', 'field2'),
        )

        obj = Mock(field_1='value 1', field2='value 2')

        res = u.fields_from_object(fields, obj)

        self.assertEqual(res,
                         (('Field 1', 'Field 2'), ['value 1', 'value 2']))

    def test_fields_from_object_xform(self):
        fields = (
            ('Field 1',),
            ('Field 2', 'field2'),
        )

        obj = Mock(field_1='value 1', field2='value 2')

        res = u.fields_from_object(fields, obj,
                                   xforms={'Field 2': lambda x: x.upper()})

        self.assertEqual(res,
                         (('Field 1', 'Field 2'), ['value 1', 'VALUE 2']))

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
