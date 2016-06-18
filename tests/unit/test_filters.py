from flask.ext.testing import TestCase
import ara.webapp as w
import ara.models as m
import datetime


class TestFilters(TestCase):
    '''Tests for our Jinja2 filters'''

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

    def test_pathtruncate_short(self):
        path = '/short/path.yml'
        self.assertTrue(len(path) < self.app.config['ARA_PATH_MAX'])

        t = self.env.from_string('{{ path | pathtruncate }}')
        res = t.render(path=path)
        self.assertEqual(res, path)
        self.assertFalse(res.startswith('...'))
        self.assertEqual(res.count('path.yml'), 1)

    def test_pathtruncate_with_length(self):
        path = '/this/is_definitely/a/very/very/long/path.yml'
        self.assertTrue(len(path) > 20)
        t = self.env.from_string('{{ path | pathtruncate(20) }}')
        res = t.render(path=path)

        self.assertNotEqual(res, path)
        self.assertTrue(res.startswith('...'))
        self.assertEqual(res.count('path.yml'), 1)

    def test_pathtruncate_long(self):
        path = '/this/is_definitely/a/very/very/long/path.yml'
        self.assertTrue(len(path) > self.app.config['ARA_PATH_MAX'])
        t = self.env.from_string('{{ path | pathtruncate }}')
        res = t.render(path=path)

        self.assertNotEqual(res, path)
        self.assertTrue(res.startswith('...'))
        self.assertEqual(res.count('path.yml'), 1)

    def test_datefmt(self):
        datestr = '2016-05-25 14:34:00'
        date = datetime.datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')
        t = self.env.from_string('{{ date | datefmt }}')
        res = t.render(date=date)

        self.assertEqual(res, datestr)

    def test_datefmt_none(self):
        t = self.env.from_string('{{ date | datefmt }}')
        res = t.render(date=None)

        self.assertEqual(res, 'n/a')

    def test_timefmt(self):
        time = datetime.timedelta(seconds=90061)
        t = self.env.from_string('{{ time | timefmt }}')
        res = t.render(time=time)

        self.assertEqual(res, '1 day, 1:01:01')

    def test_timefmt_none(self):
        t = self.env.from_string('{{ time | timefmt }}')
        res = t.render(time=None)

        self.assertEqual(res, 'n/a')

    def test_from_json(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | from_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, u"{u'key': u'value'}")

    def test_to_json(self):
        data = {'key': 'value'}
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res,
                         u'{\n    "key": "value"\n}')

    def test_to_json_fails(self):
        data = datetime.datetime.now()
        t = self.env.from_string('{{ data | to_nice_json }}')
        res = t.render(data=data)

        self.assertEqual(res, str(data))

    def test_to_json_from_string(self):
        data = '{"key": "value"}'
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res,
                         u'{\n    "key": "value"\n}')

    def test_to_json_from_invalid_string(self):
        # json.dumps does not raise exception on a non-json string,
        # it just returns an unicode string
        data = "definitely not json"
        t = self.env.from_string('{{ data | to_nice_json | safe }}')
        res = t.render(data=data)

        self.assertEqual(res, u'"definitely not json"')
