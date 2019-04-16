import logging


class User:
    def __init__(self, login):
        self.login = login

    def __eq__(self, other):
        return self.login == other


class DataBase:
    __users = [
        User('admin'),
        User('tmp_user'),
        User('me')
    ]

    @staticmethod
    def get_user(login):
        try:
            index = DataBase.__users.index(login)
            return DataBase.__users[index]
        except:
            return None
