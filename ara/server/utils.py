import os

import environ
from configobj import ConfigObj
from django.core.exceptions import ImproperlyConfigured
from everett import ConfigurationError
from everett.manager import ConfigEnvFileEnv, ConfigIniEnv, ConfigManager, ConfigOSEnv, listify

__all__ = ["EverettEnviron"]


class DumbConfigIniEnv(ConfigIniEnv):
    """Simple ConfigIniEnv with disabled list parsing that actually aborts after the first file."""

    # TODO: Remove once upstream is fixed (https://github.com/willkg/everett/pull/71)

    def __init__(self, possible_paths):
        self.cfg = {}
        possible_paths = listify(possible_paths)

        for path in possible_paths:
            if not path:
                continue

            path = os.path.abspath(os.path.expanduser(path.strip()))
            if path and os.path.isfile(path):
                self.cfg = self.parse_ini_file(path)
                break

    def parse_ini_file(cls, path):
        cfgobj = ConfigObj(path, list_values=False)

        def extract_section(namespace, d):
            cfg = {}
            for key, val in d.items():
                if isinstance(d[key], dict):
                    cfg.update(extract_section(namespace + [key], d[key]))
                else:
                    cfg["_".join(namespace + [key]).upper()] = val

            return cfg

        return extract_section([], cfgobj.dict())


class EnvironProxy:
    def __init__(self, cfg):
        self.cfg = cfg

    def __contains__(self, key):
        try:
            self.cfg(key)
        except ConfigurationError:
            return False
        return True

    def __getitem__(self, key):
        try:
            return self.cfg(key, raw_value=True)
        except ConfigurationError as err:
            raise KeyError("Missing key %r" % key) from err


class EverettEnviron(environ.Env):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ENVIRON = EnvironProxy(
            ConfigManager(
                [
                    ConfigOSEnv(),
                    ConfigEnvFileEnv(".env"),
                    DumbConfigIniEnv([os.environ.get("ARA_CFG"), "~/.config/ara/server.cfg", "/etc/ara/server.cfg"]),
                ]
            ).with_namespace("ara")
        )

    def get_value(self, var, cast=None, default=environ.Env.NOTSET, parse_default=False):
        try:
            return super().get_value(var, cast, default, parse_default)
        except ImproperlyConfigured as e:
            # Rewrite the django-environ exception to match our configs better
            if default is self.NOTSET and str(e) == "Set the {0} environment variable".format(var):
                error_msg = (
                    "Set the ARA_{0} environment variable or set {1} in the [ara] section "
                    "of your configuration file."
                ).format(var, var.lower())
                raise ImproperlyConfigured(error_msg)
            raise
