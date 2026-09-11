import socket

from loguru import logger

from OpenSSL import SSL
from tls.client import SSLClient

HOST = "127.0.0.1"
PORT = 8080
BUFFER_SIZE = 4096


class TCPClient:
    def __init__(self):
        self.tls = SSLClient()

    def debug(self):
        logger.success(f"TLS version: {connection.get_protocol_version_name()}")
        logger.success(f"TLS cipher: {connection.get_cipher_name()}")

    def start_client(self, host=HOST, port=PORT):
        global connection

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client_socket.connect((host, port))
            connection = self.tls.wrap(client_socket, host)
            connection.do_handshake()

            #self.debug()

            logger.success("Connected to {}:{}", host, port)
            logger.info("Type 'quit' to disconnect")

            while True:
                message = input("You: ")

                if message.lower() == "quit":
                    break

                if not message:
                    continue

                connection.sendall(message.encode("utf-8"))

                response = connection.recv(BUFFER_SIZE)

                if not response:
                    logger.warning("Server disconnected")
                    break

                logger.info(f"Server: {response.decode('utf-8')}")

        except ConnectionResetError:
            logger.warning("The server forcibly closed the connection")

        except ConnectionAbortedError:
            logger.warning("The connection was aborted")

        except ConnectionRefusedError:
            logger.error(f"Could not connect to {host}:{port}")

        except OSError as error:
            logger.error(f"Socket error: {error}")

        except SSL.Error as error:
            logger.error(f"SSL Error: {error}")

        finally:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            client_socket.close()
            logger.info("Connection closed")


if __name__ == "__main__":
    tcp_client = TCPClient()
    tcp_client.start_client()
