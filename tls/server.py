from OpenSSL import SSL

class SSLServer:
    def __init__(self, certfile: str, pkey: str):
        self.context = SSL.Context(SSL.TLS_SERVER_METHOD)
        self.context.use_certificate_file(certfile)
        self.context.use_privatekey_file(pkey)
        self.context.check_privatekey()

    def wrap(self, connection):
        tls = SSL.Connection(self.context, connection)
        tls.set_accept_state()
        return tls
