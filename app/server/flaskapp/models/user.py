from flaskapp.core.datastore import DataStore


class User(object):

    def __init__(self, user_id):
        self._user_id = user_id
        self._user_data = dict()
        self._datastore = DataStore()
        data = self._datastore.get(self._user_id)

        if data:
            self._user_data = data

    def set(self, key, value, auto_commit=True):
        self._user_data[key] = value
        if auto_commit:
            return self.save()

        return True

    def get(self, key):
        try:
            value = self._user_data[key]
        except KeyError:
            return None

        return value

    def pop(self, key):
        return self._user_data.pop(key, None)

    def delete(self, key):
        self._user_data.pop(key, None)
        return True

    def save(self):
        return self._datastore.put(self._user_id, self._user_data, True)

    def props(self):
        for key, value in self._user_data.items():
            yield (key, value)

    @property
    def id(self):
        return self._user_id

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._user_id})>'

    def __str__(self):
        return self._user_id

    def __nonzero__(self):
        return True if self._user_data else False

    __bool__ = __nonzero__
