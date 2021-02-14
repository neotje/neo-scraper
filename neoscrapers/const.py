class ServerConf:
    HOST = "0.0.0.0"
    PORT = 9123

class UserConf:
    USERNAME = "neo"
    EMAIL = "neo@hopjes.net"
    PASSWORD = "Neoscraper!"


SERVER_CONF = ServerConf()
# TODO: move user credential to a usermanager with database.
USER_CONF = UserConf()
