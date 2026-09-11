from OpenSSL import SSL


class SSLClient:
    def __init__(self):
        self.context = SSL.Context(SSL.TLS_CLIENT_METHOD)

    def wrap(self, connection, hostname: str):
        tls = SSL.Connection(self.context, connection)
        tls.set_connect_state()
        tls.set_tlsext_host_name(hostname.encode())
        return tls
