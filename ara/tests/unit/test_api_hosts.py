#  Copyright (c) 2017 Red Hat, Inc.
#
#  This file is part of ARA: Ansible Run Analysis.
#
#  ARA is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ARA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with ARA.  If not, see <http://www.gnu.org/licenses/>.

from ara.tests.unit.common import ansible_run
from ara.tests.unit.common import TestAra
from ara.api.hosts import HostApi
from ara.api.v1.hosts import HOST_FIELDS
import ara.db.models as models
import pytest

from oslo_serialization import jsonutils
from werkzeug.routing import RequestRedirect


class TestApiHosts(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiHosts, self).setUp()

    def tearDown(self):
        super(TestApiHosts, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_http_redirect(self):
        res = self.client.post('/api/v1/hosts')
        self.assertEqual(res.status_code, 301)

    def test_post_http_with_no_data(self):
        res = self.client.post('/api/v1/hosts/',
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_no_data(self):
        res = HostApi().post()
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_correct_data(self):
        # Create fake playbook data and create a host in it
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "name": "hostname",
            "facts": {
                "ansible_foo": "bar"
            },
            "changed": 1,
            "failed": 0,
            "ok": 4,
            "skipped": 1,
            "unreachable": 0
        }
        res = self.client.post('/api/v1/hosts/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full host object ("data")
        # and that the host was really created properly by fetching it
        # ("host")
        host = self.client.get('/api/v1/hosts/',
                               content_type='application/json',
                               query_string=dict(id=data['id']))
        host = jsonutils.loads(host.data)
        self.assertEqual(len(data), len(host))
        self.assertEqual(data, host)
        for key in HOST_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, host)

    def test_post_internal_with_correct_data(self):
        # Create fake playbook data and create a host in it
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "name": "hostname",
            "facts": {
                "ansible_foo": "bar"
            },
            "changed": 1,
            "failed": 0,
            "ok": 4,
            "skipped": 1,
            "unreachable": 0
        }
        res = HostApi().post(data)
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full host object ("data")
        # and that the host was really created properly by fetching it
        # ("host")
        host = HostApi().get(id=data['id'])
        host = jsonutils.loads(host.data)
        self.assertEqual(len(data), len(host))
        self.assertEqual(data, host)
        for key in HOST_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, host)

    def test_post_http_with_incorrect_data(self):
        data = {
            "playbook_id": "1",
            "name": 1,
            "facts": False,
            "changed": False
        }

        res = self.client.post('/api/v1/hosts/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_incorrect_data(self):
        data = {
            "playbook_id": "1",
            "name": 1,
            "facts": False,
            "changed": False
        }

        res = HostApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_missing_argument(self):
        data = {
            "name": "hostname",
        }
        res = self.client.post('/api/v1/hosts/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_missing_argument(self):
        data = {
            "name": "hostname",
        }
        res = HostApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_nonexistant_playbook(self):
        data = {
            "playbook_id": 9001,
            "name": "hostname",
        }
        res = self.client.post('/api/v1/hosts/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 404)

    def test_post_internal_with_nonexistant_playbook(self):
        data = {
            "playbook_id": 9001,
            "name": "hostname",
        }
        res = HostApi().post(data)
        self.assertEqual(res.status_code, 404)

    ###########
    # PATCH
    ###########
    def test_patch_http_redirect(self):
        res = self.client.patch('/api/v1/hosts')
        self.assertEqual(res.status_code, 301)

    def test_patch_http_with_no_data(self):
        res = self.client.patch('/api/v1/hosts/',
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_no_data(self):
        res = HostApi().patch()
        self.assertEqual(res.status_code, 400)

    def test_patch_http_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['host'].id, 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated host name"
        self.assertNotEqual(ctx['host'].name, new_name)

        data = {
            "id": ctx['host'].id,
            "name": new_name
        }
        res = self.client.patch('/api/v1/hosts/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching host
        updated = self.client.get('/api/v1/hosts/',
                                  content_type='application/json',
                                  query_string=dict(id=ctx['host'].id))
        updated_host = jsonutils.loads(updated.data)
        self.assertEqual(updated_host['name'], new_name)

    def test_patch_internal_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['host'].id, 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_name = "Updated host name"
        self.assertNotEqual(ctx['host'].name, new_name)

        data = {
            "id": ctx['host'].id,
            "name": new_name
        }
        res = HostApi().patch(data)
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['name'], new_name)

        # Confirm by re-fetching host
        updated = HostApi().get(id=ctx['host'].id)
        updated_host = jsonutils.loads(updated.data)
        self.assertEqual(updated_host['name'], new_name)

    def test_patch_http_with_missing_arg(self):
        ansible_run()
        data = {
            "name": "Updated host name"
        }
        res = self.client.patch('/api/v1/hosts/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_missing_arg(self):
        ansible_run()
        data = {
            "name": "Updated host name"
        }
        res = HostApi().patch(data)
        self.assertEqual(res.status_code, 400)

    ###########
    # PUT
    ###########
    def test_put_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.put('/api/v1/hosts')

    # Not implemented yet
    def test_put_http_unimplemented(self):
        res = self.client.put('/api/v1/hosts/')
        self.assertEqual(res.status_code, 405)

    def test_put_internal_unimplemented(self):
        http = self.client.put('/api/v1/hosts/')
        internal = HostApi().put()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # DELETE
    ###########
    def test_delete_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.delete('/api/v1/hosts')

    # Not implemented yet
    def test_delete_http_unimplemented(self):
        res = self.client.delete('/api/v1/hosts/')
        self.assertEqual(res.status_code, 405)

    def test_delete_internal_unimplemented(self):
        http = self.client.delete('/api/v1/hosts/')
        internal = HostApi().delete()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # GET
    ###########
    def test_get_http_redirect(self):
        res = self.client.get('/api/v1/hosts',
                              content_type='application/json')
        self.assertEqual(res.status_code, 301)

    def test_get_http_with_bad_params_404_help(self):
        res = self.client.get('/api/v1/hosts/',
                              content_type='application/json',
                              query_string=dict(id=0))
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_with_bad_params_404_help(self):
        http = self.client.get('/api/v1/hosts/',
                               content_type='application/json',
                               query_string=dict(id=0))
        internal = HostApi().get(id=0)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters_and_data(self):
        res = self.client.get('/api/v1/hosts/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_without_parameters_and_data(self):
        http = self.client.get('/api/v1/hosts/',
                               content_type='application/json')
        internal = HostApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters(self):
        ctx = ansible_run()
        res = self.client.get('/api/v1/hosts/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)[0]

        self.assertEqual(ctx['host'].id,
                         data['id'])
        self.assertEqual(ctx['host'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['host'].name,
                         data['name'])
        self.assertEqual(ctx['host'].facts,
                         data['facts'])
        self.assertEqual(ctx['host'].changed,
                         data['changed'])
        self.assertEqual(ctx['host'].failed,
                         data['failed'])
        self.assertEqual(ctx['host'].ok,
                         data['ok'])
        self.assertEqual(ctx['host'].skipped,
                         data['skipped'])
        self.assertEqual(ctx['host'].unreachable,
                         data['unreachable'])

    def test_get_internal_without_parameters(self):
        ansible_run()
        http = self.client.get('/api/v1/hosts/',
                               content_type='application/json')
        internal = HostApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        hosts = models.Host.query.all()
        self.assertEqual(len(hosts), 2)

        res = self.client.get('/api/v1/hosts/',
                              content_type='application/json',
                              query_string=dict(id=1))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['host'].id,
                         data['id'])
        self.assertEqual(ctx['host'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['host'].name,
                         data['name'])
        self.assertEqual(ctx['host'].facts,
                         data['facts'])
        self.assertEqual(ctx['host'].changed,
                         data['changed'])
        self.assertEqual(ctx['host'].failed,
                         data['failed'])
        self.assertEqual(ctx['host'].ok,
                         data['ok'])
        self.assertEqual(ctx['host'].skipped,
                         data['skipped'])
        self.assertEqual(ctx['host'].unreachable,
                         data['unreachable'])

    def test_get_internal_with_id_parameter(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        hosts = models.Host.query.all()
        self.assertEqual(len(hosts), 2)

        http = self.client.get('/api/v1/hosts/',
                               content_type='application/json',
                               query_string=dict(id=1))
        internal = HostApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        hosts = models.Host.query.all()
        self.assertEqual(len(hosts), 2)

        res = self.client.get('/api/v1/hosts/1',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['host'].id,
                         data['id'])
        self.assertEqual(ctx['host'].playbook_id,
                         data['playbook_id'])
        self.assertEqual(ctx['host'].name,
                         data['name'])
        self.assertEqual(ctx['host'].facts,
                         data['facts'])
        self.assertEqual(ctx['host'].changed,
                         data['changed'])
        self.assertEqual(ctx['host'].failed,
                         data['failed'])
        self.assertEqual(ctx['host'].ok,
                         data['ok'])
        self.assertEqual(ctx['host'].skipped,
                         data['skipped'])
        self.assertEqual(ctx['host'].unreachable,
                         data['unreachable'])

    def test_get_internal_with_id_url(self):
        ansible_run()
        # Run twice to get a second playbook
        ansible_run()
        hosts = models.Host.query.all()
        self.assertEqual(len(hosts), 2)

        http = self.client.get('/api/v1/hosts/1',
                               content_type='application/json')
        internal = HostApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
