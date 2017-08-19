# -*- coding: utf-8 -*-
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
from ara.api.files import FileApi
from ara.api.v1.files import FILE_FIELDS
import ara.db.models as models
import pytest

from oslo_serialization import jsonutils
from werkzeug.routing import RequestRedirect


class TestApiFiles(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestApiFiles, self).setUp()

    def tearDown(self):
        super(TestApiFiles, self).tearDown()

    ###########
    # POST
    ###########
    def test_post_http_redirect(self):
        res = self.client.post('/api/v1/files')
        self.assertEqual(res.status_code, 301)

    def test_post_http_with_no_data(self):
        res = self.client.post('/api/v1/files/',
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_no_data(self):
        res = FileApi().post()
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_correct_data(self):
        # Create fake playbook data and create a file in it
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "path": "/root/playbook.yml",
            "content": "---\n- name: A task from ünit tests"
        }
        res = self.client.post('/api/v1/files/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full file object ("data")
        # and that the file was really created properly by fetching it
        # ("file")
        file_ = self.client.get('/api/v1/files/',
                                content_type='application/json',
                                query_string=dict(id=data['id']))
        file_ = jsonutils.loads(file_.data)
        self.assertEqual(len(data), len(file_))
        self.assertEqual(data, file_)
        for key in FILE_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, file_)

    def test_post_internal_with_correct_data(self):
        # Create fake playbook data and create a file in it
        ctx = ansible_run()
        data = {
            "playbook_id": ctx['playbook'].id,
            "path": "/root/playbook.yml",
            "content": "---\n- name: A task from ünit tests"
        }
        res = FileApi().post(data)
        self.assertEqual(res.status_code, 200)
        data = jsonutils.loads(res.data)

        # Confirm that the POST returned the full file object ("data")
        # and that the file was really created properly by fetching it
        # ("file")
        file_ = FileApi().get(id=data['id'])
        file_ = jsonutils.loads(file_.data)
        self.assertEqual(len(data), len(file_))
        self.assertEqual(data, file_)
        for key in FILE_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, file_)

    def test_post_http_with_incorrect_data(self):
        data = {
            "playbook_id": "1",
            "path": False,
            "content": 1,
        }

        res = self.client.post('/api/v1/files/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_incorrect_data(self):
        data = {
            "playbook_id": "1",
            "path": False,
            "content": 1,
        }

        res = FileApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_missing_argument(self):
        data = {
            "path": "/root/playbook.yml",
            "content": """
                    ---
                    - name: A task from ünit tests
                      debug:
                        msg: "hello world"
                    """
        }
        res = self.client.post('/api/v1/files/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_post_internal_with_missing_argument(self):
        data = {
            "path": "/root/playbook.yml",
            "content": """
                    ---
                    - name: A task from ünit tests
                      debug:
                        msg: "hello world"
                    """
        }
        res = FileApi().post(data)
        self.assertEqual(res.status_code, 400)

    def test_post_http_with_nonexistant_playbook(self):
        ansible_run()
        data = {
            "playbook_id": 9001,
            "path": "/root/playbook.yml",
            "content": """
                    ---
                    - name: A task from ünit tests
                      debug:
                        msg: "hello world"
                    """
        }
        res = self.client.post('/api/v1/files/',
                               data=jsonutils.dumps(data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 404)

    def test_post_internal_with_nonexistant_playbook(self):
        ansible_run()
        data = {
            "playbook_id": 9001,
            "path": "/root/playbook.yml",
            "content": """
                    ---
                    - name: A task from ünit tests
                      debug:
                        msg: "hello world"
                    """
        }
        res = FileApi().post(data)
        self.assertEqual(res.status_code, 404)

    ###########
    # PATCH
    ###########
    def test_patch_http_redirect(self):
        res = self.client.patch('/api/v1/files')
        self.assertEqual(res.status_code, 301)

    def test_patch_http_with_no_data(self):
        res = self.client.patch('/api/v1/files/',
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_no_data(self):
        res = FileApi().patch()
        self.assertEqual(res.status_code, 400)

    def test_patch_http_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['playbook'].file.id, 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_content = "# Empty file !"
        self.assertNotEqual(ctx['playbook'].file.content, new_content)

        data = {
            "id": ctx['playbook'].file.id,
            "content": new_content
        }
        res = self.client.patch('/api/v1/files/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['content'], new_content)

        # Confirm by re-fetching file
        updated = self.client.get('/api/v1/files/',
                                  content_type='application/json',
                                  query_string=dict(
                                      id=ctx['playbook'].file.id)
                                  )
        updated_file = jsonutils.loads(updated.data)
        self.assertEqual(updated_file['content'], new_content)

    def test_patch_internal_existing(self):
        # Generate fake playbook data
        ctx = ansible_run()
        self.assertEqual(ctx['playbook'].file.id, 1)

        # We'll update the name field, assert we are actually
        # making a change
        new_content = "# Empty file !"
        self.assertNotEqual(ctx['playbook'].file.content, new_content)

        data = {
            "id": ctx['playbook'].file.id,
            "content": new_content
        }
        res = FileApi().patch(data)
        self.assertEqual(res.status_code, 200)

        # The patch endpoint should return the full updated object
        data = jsonutils.loads(res.data)
        self.assertEqual(data['content'], new_content)

        # Confirm by re-fetching file
        updated = FileApi().get(id=ctx['playbook'].file.id)
        updated_file = jsonutils.loads(updated.data)
        self.assertEqual(updated_file['content'], new_content)

    def test_patch_http_with_missing_arg(self):
        ansible_run()
        data = {
            "path": "/updated/path.yml"
        }
        res = self.client.patch('/api/v1/files/',
                                data=jsonutils.dumps(data),
                                content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_patch_internal_with_missing_arg(self):
        ansible_run()
        data = {
            "path": "/updated/path.yml"
        }
        res = FileApi().patch(data)
        self.assertEqual(res.status_code, 400)

    ###########
    # PUT
    ###########
    def test_put_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.put('/api/v1/files')

    # Not implemented yet
    def test_put_http_unimplemented(self):
        res = self.client.put('/api/v1/files/')
        self.assertEqual(res.status_code, 405)

    def test_put_internal_unimplemented(self):
        http = self.client.put('/api/v1/files/')
        internal = FileApi().put()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # DELETE
    ###########
    def test_delete_http_redirect(self):
        # TODO: Does this raise a RequestRedirect due to underlying 405 ?
        with pytest.raises(RequestRedirect):
            self.client.delete('/api/v1/files')

    # Not implemented yet
    def test_delete_http_unimplemented(self):
        res = self.client.delete('/api/v1/files/')
        self.assertEqual(res.status_code, 405)

    def test_delete_internal_unimplemented(self):
        http = self.client.delete('/api/v1/files/')
        internal = FileApi().delete()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    ###########
    # GET
    ###########
    def test_get_http_redirect(self):
        res = self.client.get('/api/v1/files',
                              content_type='application/json')
        self.assertEqual(res.status_code, 301)

    def test_get_http_with_bad_params_404_help(self):
        res = self.client.get('/api/v1/files/',
                              content_type='application/json',
                              query_string=dict(id=0))
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_with_bad_params_404_help(self):
        http = self.client.get('/api/v1/files/',
                               content_type='application/json',
                               query_string=dict(id=0))
        internal = FileApi().get(id=0)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters_and_data(self):
        res = self.client.get('/api/v1/files/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 404)
        # TODO: Improve this
        self.assertTrue(b'result_output' in res.data)
        self.assertTrue(b'query_parameters' in res.data)

    def test_get_internal_without_parameters_and_data(self):
        http = self.client.get('/api/v1/files/',
                               content_type='application/json')
        internal = FileApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_without_parameters(self):
        ctx = ansible_run()
        res = self.client.get('/api/v1/files/',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)[1]

        self.assertEqual(ctx['playbook'].file.id,
                         data['id'])
        self.assertEqual(ctx['playbook'].file.playbook_id,
                         data['playbook']['id'])
        self.assertEqual(ctx['playbook'].file.path,
                         data['path'])
        self.assertEqual(ctx['playbook'].file.content.content,
                         data['content'])
        self.assertEqual(ctx['playbook'].file.content.sha1,
                         data['sha1'])
        self.assertEqual(ctx['playbook'].file.is_playbook,
                         data['is_playbook'])

    def test_get_internal_without_parameters(self):
        ansible_run()
        http = self.client.get('/api/v1/files/',
                               content_type='application/json')
        internal = FileApi().get()
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_parameter(self):
        ctx = ansible_run()
        files = models.File.query.all()
        self.assertEqual(len(files), 2)

        res = self.client.get('/api/v1/files/',
                              content_type='application/json',
                              query_string=dict(id=1))
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['playbook'].file.id,
                         data['id'])
        self.assertEqual(ctx['playbook'].file.playbook_id,
                         data['playbook']['id'])
        self.assertEqual(ctx['playbook'].file.path,
                         data['path'])
        self.assertEqual(ctx['playbook'].file.content.content,
                         data['content'])
        self.assertEqual(ctx['playbook'].file.content.sha1,
                         data['sha1'])
        self.assertEqual(ctx['playbook'].file.is_playbook,
                         data['is_playbook'])

    def test_get_internal_with_id_parameter(self):
        ansible_run()
        files = models.File.query.all()
        self.assertEqual(len(files), 2)

        http = self.client.get('/api/v1/files/',
                               content_type='application/json',
                               query_string=dict(id=1))
        internal = FileApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)

    def test_get_http_with_id_url(self):
        ctx = ansible_run()
        files = models.File.query.all()
        self.assertEqual(len(files), 2)

        res = self.client.get('/api/v1/files/1',
                              content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = jsonutils.loads(res.data)
        self.assertEqual(ctx['playbook'].file.id,
                         data['id'])
        self.assertEqual(ctx['playbook'].file.playbook_id,
                         data['playbook']['id'])
        self.assertEqual(ctx['playbook'].file.path,
                         data['path'])
        self.assertEqual(ctx['playbook'].file.content.content,
                         data['content'])
        self.assertEqual(ctx['playbook'].file.content.sha1,
                         data['sha1'])
        self.assertEqual(ctx['playbook'].file.is_playbook,
                         data['is_playbook'])

    def test_get_internal_with_id(self):
        ansible_run()
        files = models.File.query.all()
        self.assertEqual(len(files), 2)

        http = self.client.get('/api/v1/files/1',
                               content_type='application/json')
        internal = FileApi().get(id=1)
        self.assertEqual(http.status_code, internal.status_code)
        self.assertEqual(http.data, internal.data)
