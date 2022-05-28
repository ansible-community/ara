# Copyright (c) 2022 The ARA Records Ansible authors
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings

from ara.api.auth import APIAccessPermission


class User:
    is_authenticated = True


class AnonymousUser(User):
    is_authenticated = False


class PermissionBackendTestCase(TestCase):
    def setUp(self):
        factory = RequestFactory()
        self.anon_get_request = factory.get("/")
        self.anon_get_request.user = AnonymousUser()
        self.anon_post_request = factory.post("/")
        self.anon_post_request.user = AnonymousUser()

        self.authed_get_request = factory.get("/")
        self.authed_get_request.user = User()
        self.authed_post_request = factory.post("/")
        self.authed_post_request.user = User()

    @override_settings(READ_LOGIN_REQUIRED=False, WRITE_LOGIN_REQUIRED=True)
    def test_anonymous_read_access(self):
        backend = APIAccessPermission()

        # Writes are blocked (just to show it has no affect on read)
        self.assertFalse(backend.has_permission(self.anon_post_request, None))

        # Reads are allowed based on READ_LOGIN_REQUIRED
        self.assertTrue(backend.has_permission(self.anon_get_request, None))
        settings.READ_LOGIN_REQUIRED = True
        self.assertFalse(backend.has_permission(self.anon_get_request, None))

    @override_settings(READ_LOGIN_REQUIRED=True, WRITE_LOGIN_REQUIRED=False)
    def test_anonymous_write_access(self):
        backend = APIAccessPermission()

        # Reads are blocked (just to show it has no affect on write)
        self.assertFalse(backend.has_permission(self.anon_get_request, None))

        # Writes are allowed based on WRITE_LOGIN_REQUIRED
        self.assertTrue(backend.has_permission(self.anon_post_request, None))
        settings.WRITE_LOGIN_REQUIRED = True
        self.assertFalse(backend.has_permission(self.anon_post_request, None))

    @override_settings(READ_LOGIN_REQUIRED=True, WRITE_LOGIN_REQUIRED=True)
    def test_auth_access(self):
        backend = APIAccessPermission()

        self.assertTrue(backend.has_permission(self.authed_get_request, None))
        self.assertTrue(backend.has_permission(self.authed_post_request, None))
