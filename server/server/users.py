"""
Users resource to handle registered users and their profiles
"""

from server.api import Api
from server.resource import Resource
from server.resource_helpers import ( expect_data,
                                      expect_session_key,
                                      verify_username,
                                      verify_user,
                                    )

class UserConfig(object):
    def __init__(self):
        self.blocked = []
        self.chat_filter = Api.default_chat_filter

    def get_dict(self):
        return {
            Api.blocked: self.blocked,
            Api.chat_filter: self.chat_filter,
        }

class UserProfile(object):
    def __init__(self):
        self.firstname = ""
        self.lastname = ""
        self.bio = ""
        self.gender = ""

    def get_dict(self):
        return {
            Api.firstname: self.firstname,
            Api.lastname: self.lastname,
            Api.bio: self.bio,
            Api.gender: self.gender,
        }

class User(object):
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.config = UserConfig()
        self.profile = UserProfile()

class Users(Resource):
    """
    Resource Parameters
    """

    """
    Resource Data
    """
    def __init__(self):
        self._users = {} # Key: username, Value: User()
        self.session = None
        self.users = self

    """
    Resource Methods
    """
    def validate_username(self, username):
        return username in self._users

    def set_session_resource(self, session_resource):
        self.session = session_resource

    def validate_password(self, username, password):
        return password == self._users[username].password

    """
    Special Uri Handling
    """
    method_uris = {
        'on_put_change_password': Api.username_param + Api.res_password,
        'on_put_verify_email': Api.username_param + Api.res_emails,
        'on_get_user_config': Api.username_param + Api.res_config,
        'on_put_user_config': Api.username_param + Api.res_config,
        'on_get_user_profile': Api.username_param + Api.res_profile,
        'on_put_user_profile': Api.username_param + Api.res_profile,
    }

    """
    Rest Methods
    """
    @expect_data(Api.username, Api.password, Api.email)
    def on_post_register(self, username, password, email):
        # TODO: validate email, send email
        if username not in self._users:
            self._users[username] = User(username, password, email)
            self.response.status = 201
        else:
            self.response.status = 409
        return {}

    @expect_session_key
    @expect_data(Api.password)
    @verify_username
    def on_put_change_password(self, session_key, password, username):
        self._users[username].password = password
        self.session.logout_user(username)
        self.response.status = 200
        return {}

    @expect_data(Api.email, Api.email_code)
    @verify_username
    def on_put_verify_email(self, email, email_code, username):
        # TODO: implement this code stuff
        user = self._users[username]
        if user.email == email:
            self.response.status = 200
            return {}
        else:
            self.response.status = 422
            return {}

    @expect_session_key
    @verify_username
    def on_get_user_config(self, session_key, username):
        user = self._users[username]
        self.response.status = 200
        return user.config.get_dict()

    @expect_session_key
    @verify_username
    def on_put_user_config(self, session_key, username):
        user = self._users[username]
        json_data = self.request.json
        if Api.blocked in json_data:
            user.config.blocked = json_data[Api.blocked]
        if Api.chat_filter in json_data:
            user.config.chat_filter = json_data[Api.chat_filter]

        self.response.status = 200
        return user.config.get_dict()

    @expect_session_key
    @verify_user
    def on_get_user_profile(self, session_key, username):
        self.response.status = 200
        return self._users[username].profile.get_dict()

    @expect_session_key
    @verify_username
    def on_put_user_profile(self, session_key, username):
        user = self._users[username]
        json_data = self.request.json
        if Api.firstname in json_data:
            user.profile.firstname = json_data[Api.firstname]
        if Api.lastname in json_data:
            user.profile.lastname = json_data[Api.lastname]
        if Api.bio in json_data:
            user.profile.bio = json_data[Api.bio]
        if Api.gender in json_data:
            user.profile.gender = json_data[Api.gender]

        return user.profile.get_dict()

