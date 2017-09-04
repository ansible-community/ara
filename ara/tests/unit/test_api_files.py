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

from ara.tests.unit.fakes import FakeRun
from ara.tests.unit.common import TestAra
from ara.api.files import FileApi
from ara.api.v1.files import FILE_FIELDS


class TestPythonApiFiles(TestAra):
    """ Tests for the ARA API interface """
    def setUp(self):
        super(TestPythonApiFiles, self).setUp()
        self.client = FileApi()

    def tearDown(self):
        super(TestPythonApiFiles, self).tearDown()

    ###########
    # POST
    ###########
    # TODO: Add test for validating that is_playbook is set properly for
    # playbook files
    def test_post_with_no_data(self):
        resp, data = self.client.post()
        self.assertEqual(resp.status_code, 400)

    def test_post_with_correct_data(self):
        # Create fake playbook data and create a file in it
        ctx = FakeRun()
        resp, file_ = self.client.post(
            playbook_id=ctx.playbook['id'],
            path='/root/playbook.yml',
            content='---\n- name: Task from ünit tests'
        )
        self.assertEqual(resp.status_code, 200)

        # Confirm that the POST returned the full file object ("data")
        # and that the file was really created properly by fetching it
        # ("file")
        resp, data = self.client.get(id=file_['id'])
        self.assertEqual(len(data), len(file_))
        self.assertEqual(data, file_)
        for key in FILE_FIELDS.keys():
            self.assertIn(key, data)
            self.assertIn(key, file_)

    def test_post_with_incorrect_data(self):
        FakeRun()
        resp, data = self.client.post(
            playbook_id='1',
            path=False,
            content=1
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_missing_argument(self):
        FakeRun()
        resp, data = self.client.post(
            path='/root/playbook.yml',
            content='hello world'
        )
        self.assertEqual(resp.status_code, 400)

    def test_post_with_nonexistant_playbook(self):
        resp, data = self.client.post(
            playbook_id=9001,
            path='/root/playbook.yml',
            content='hello world'
        )
        self.assertEqual(resp.status_code, 404)

    def test_post_file_already_exists(self):
        # Posting the same file a second time should yield a 200 and not error
        # out, files are unique per sha1
        ctx = FakeRun()

        # Retrieve the playbook file so we can post the same thing
        resp, pbfile = self.client.get(
            playbook_id=ctx.playbook['id'],
            is_playbook=True
        )
        pbfile = pbfile[0]

        # Post the same thing
        resp, data = self.client.post(
            playbook_id=pbfile['playbook']['id'],
            path=pbfile['path'],
            content=pbfile['content']
        )

        self.assertEqual(resp.status_code, 200)
        file_ = data

        self.assertEqual(pbfile['sha1'], file_['sha1'])

    ###########
    # PATCH
    ###########
    def test_patch_with_no_data(self):
        resp, data = self.client.patch()
        self.assertEqual(resp.status_code, 400)

    def test_patch_existing(self):
        # Generate fake playbook data
        ctx = FakeRun()
        self.assertEqual(ctx.playbook['files'][0]['id'], 1)

        # Get existing file
        resp, file_ = self.client.get(id=ctx.playbook['files'][0]['id'])

        # We'll update the content field, assert we are actually
        # making a change
        new_content = '# Empty file !'
        self.assertNotEqual(file_['content'], new_content)

        resp, data = self.client.patch(
            id=file_['id'],
            content=new_content
        )
        self.assertEqual(resp.status_code, 200)

        # The patch endpoint should return the full updated object
        self.assertEqual(data['content'], new_content)

        # Confirm by re-fetching file
        resp, updated = self.client.get(id=file_['id'])
        self.assertEqual(updated['content'], new_content)

    def test_patch_with_missing_arg(self):
        resp, data = self.client.patch(path='/updated/path.yml')
        self.assertEqual(resp.status_code, 400)

    ###########
    # PUT
    ###########
    # Not implemented yet
    def test_put_unimplemented(self):
        resp, data = self.client.put()
        self.assertEqual(resp.status_code, 405)

    ###########
    # DELETE
    ###########
    # Not implemented yet
    def test_delete_unimplemented(self):
        resp, data = self.client.delete()
        self.assertEqual(resp.status_code, 405)

    ###########
    # GET
    ###########
    def test_get_with_bad_params_404_help(self):
        FakeRun()
        resp, data = self.client.get(id=0)
        self.assertEqual(resp.status_code, 404)
        # TODO: Improve this
        self.assertTrue('result_output' in data['help'])
        self.assertTrue('query_parameters' in data['help'])

    def test_get_without_parameters_and_data(self):
        resp, data = self.client.get()
        self.assertEqual(resp.status_code, 404)
        # TODO: Improve this
        self.assertTrue('result_output' in data['help'])
        self.assertTrue('query_parameters' in data['help'])

    def test_get_http_without_parameters(self):
        ctx = FakeRun()
        resp, data = self.client.get()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(ctx.playbook['files']),
                         len(data))

        data = data[0]

        self.assertEqual(ctx.playbook['files'][0]['id'], data['id'])
        self.assertEqual(ctx.playbook['id'], data['playbook']['id'])
        self.assertEqual(ctx.playbook['path'], data['path'])

    def test_get_with_id_parameter(self):
        # Run twice and assert that we have two files
        ctx = FakeRun()
        FakeRun()
        resp, files = self.client.get()
        self.assertEqual(len(files), 2)

        # Get the file from our first playbook run
        resp, data = self.client.get(id=1)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ctx.playbook['files'][0]['id'], data['id'])
        self.assertEqual(ctx.playbook['id'], data['playbook']['id'])
        self.assertEqual(ctx.playbook['path'], data['path'])
