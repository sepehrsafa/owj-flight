class Login:
    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.airline = self.config.airline
        self.username = self.config.username
        self.password = self.config.password

    def _set_session_cookie(self):

        status, text, headers = self.config.get('xbe/private/showXBEMain.action')
        if status != 200:
            return False
        return True

    def login(self):
        if(not self._set_session_cookie()):
            return False
        data = {
            'j_username': self.username,
            'j_password': self.password,
        }
        additional_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{self.config.site_url}/xbe/private/showXBEMain.action'
        }
        status, text, headers = self.config.post_form('xbe/public/j_security_check', data=data, headers=additional_headers)
        if status != 200:
            return False
        return True
