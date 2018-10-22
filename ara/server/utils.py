import os

import environ
from everett import ConfigurationError
from everett.manager import ConfigEnvFileEnv, ConfigIniEnv, ConfigManager, ConfigOSEnv

__all__ = ["EverettEnviron"]


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
            return self.cfg(key)
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
                    ConfigIniEnv([os.environ.get("ARA_CFG"), "~/.config/ara/server.cfg", "/etc/ara/server.cfg"]),
                ]
            ).with_namespace("ara")
        )
