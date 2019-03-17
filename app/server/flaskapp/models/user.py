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

    def get(self, key, raise_on_missing=False):
        try:
            value = self._user_data[key]
        except KeyError:
            if raise_on_missing:
                raise KeyError(f'User object has no key named "{key}"')
            return None

        return value

    def pop(self, key, auto_commit=True):
        if auto_commit:
            return self.save()
        return self._user_data.pop(key, None)

    def delete(self, key, auto_commit=True):
        if auto_commit:
            return self.save()
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
