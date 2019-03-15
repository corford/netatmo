import sys
# Prevent import of transparent C optimised pickle module (since
# we're running in green threads on prod)
sys.modules['_pickle'] = None  # noqa: E402

import pickle
import redis
import collections
import textwrap

from flask import current_app as app

DatastoreHost = collections.namedtuple(
                    'DatastoreHost',
                    ['plugin', 'addr', 'port', 'db', 'user', 'pwd'])


class DataStore(object):

    def __init__(
            self,
            plugin=None,
            host=None,
            port=None,
            db=None,
            user=None,
            pwd=None):

        self._host = DatastoreHost(
            plugin if plugin is not None else app.config['STORAGE_PLUGIN'],
            host if host is not None else app.config['STORAGE_HOST'],
            port if port is not None else app.config['STORAGE_PORT'],
            db if db is not None else app.config['STORAGE_DB'],
            user if user is not None else app.config['STORAGE_USER'],
            pwd if pwd is not None else app.config['STORAGE_PWD'])

        self._store = self._connect(self._host)

    def _connect(self, host):
        if host.plugin == 'redis':
            return RedisStoragePlugin(host)
        else:
            raise NotImplementedError(
                f'"{host.plugin}"'
                f'is not a recognised storage plugin')

    def put(self, record_id, record, overwrite=False):
        return self._store.put(record_id, record, overwrite)

    def get(self, record_id):
        return self._store.get(record_id)

    def pop(self, record_id):
        return self._store.pop(record_id)

    def delete(self, record_id):
        return self._store.delete(record_id)

    @property
    def host_info(self):
        return self._host

    def __repr__(self):
        return (f'<{self.__class__.__name__}('
                f'plugin={self._host.plugin},'
                f'host={self._host.addr},'
                f'port={self._host.port},'
                f'db={self._host.db},'
                f'user={self._host.user},'
                f'pwd={self._host.pwd})>')

    def __str__(self):
        return f'{self.__class__.__name__}'


class DataStorePluginInterface(object):

    def __init__(self, host):
        self._host = host

    def put(self, record_id, record, overwrite=False):
        raise NotImplementedError()

    def get(self, record_id):
        raise NotImplementedError()

    def pop(self, record_id):
        raise NotImplementedError()

    def delete(self, record_id):
        raise NotImplementedError()


class RedisStoragePlugin(DataStorePluginInterface):

    def __init__(self, host):
        super(RedisStoragePlugin, self).__init__(host)

        self._db = redis.Redis(
                        host=self._host.addr,
                        port=self._host.port,
                        db=self._host.db,
                        password=self._host.pwd)

    def put(self, record_id, record, overwrite=False):
        if not isinstance(record_id, str):
            raise TypeError('"record_id" must be a unicode string')

        key = record_id.encode('utf-8')
        value = pickle.dumps(
                    record,
                    protocol=4)  # Pickle automatically encodes to 8bit ASCII

        if overwrite is False and self._db.exists(key):
            app.logger.info(
                '[REDIS] Could not set key %r '
                'with value: %r (key already exists)',
                key, value)

            return False

        app.logger.debug('[REDIS] Setting key %r with value: %r', key, value)
        self._db.set(key, value)

        return True

    def get(self, record_id):
        if not isinstance(record_id, str):
            raise TypeError('"record_id" must be a unicode string')

        key = record_id.encode('utf-8')
        app.logger.debug('[REDIS] Getting value for key: %r', key)
        result = self._db.get(key)

        if result is not None:
            app.logger.debug(
                '[REDIS] Get operation succeeded. '
                'Data returned was: %r', result)
            result = pickle.loads(
                        result)  # Pickle automatically decodes to unicode

        else:
            app.logger.debug('[REDIS] Get operation failed for key: %r', key)

        return result

    def pop(self, record_id):
        if not isinstance(record_id, str):
            raise TypeError('"record_id" must be a unicode string')

        lua = textwrap.dedent('''\
            local value = redis.call('GET', KEYS[1])
            redis.call('DEL', KEYS[1])
            return value
            ''')

        pop = self._db.register_script(lua)
        key = record_id.encode('utf-8')

        app.logger.debug('[REDIS] Popping key: %r', key)
        value = pop(keys=[key])

        return None if value is None else pickle.loads(value)

    def delete(self, record_id):
        if not isinstance(record_id, str):
            raise TypeError('"record_id" must be a unicode string')

        key = record_id.encode('utf-8')

        app.logger.debug('[REDIS] Deleting key: %r', key)

        self._db.delete(key)

        return True

    def __repr__(self):
        return fr'<{self.__class__.__name__}({self._host})>'

    def __str__(self):
        return f'{self.__class__.__name__}'
