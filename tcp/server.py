import asyncio
import ssl
from loguru import logger
from pathlib import Path


HOST = "0.0.0.0"
PORT = 8080
BACKLOG = 128
BUFFER_SIZE = 4096

BASE_DIR = Path(__file__).resolve().parent.parent

CERTFILE = str(BASE_DIR / "certifications" / "certfile.crt")
PKEY = str(BASE_DIR / "certifications" / "pkey.key")


def build_ssl_context(certfile: str, keyfile: str) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return context


class TCPServer:
    def __init__(self):
        self.active_clients = 0
        self.active_clients_lock = asyncio.Lock()
        self.ssl_context = build_ssl_context(str(CERTFILE), str(PKEY))

    async def handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        client_address = writer.get_extra_info("peername")

        async with self.active_clients_lock:
            self.active_clients += 1
            current_clients = self.active_clients

        logger.success(
            "Client connected: {} | Active clients: {}",
            client_address,
            current_clients,
        )

        try:
            while True:
                data = await reader.read(BUFFER_SIZE)

                if not data:
                    break

                try:
                    message = data.decode("utf-8")
                except UnicodeDecodeError:
                    logger.warning(
                        "Invalid UTF-8 data received from {}",
                        client_address,
                    )
                    writer.write(b"Server error: invalid UTF-8 data")
                    await writer.drain()
                    continue

                logger.info(
                    "Received from {}: {}",
                    client_address,
                    message,
                )

                response = f"Server received: {message}"

                writer.write(response.encode("utf-8"))
                await writer.drain()

        except ConnectionResetError:
            logger.warning(
                "Client forcibly disconnected: {}",
                client_address,
            )

        except BrokenPipeError:
            logger.warning(
                "Broken pipe: {}",
                client_address,
            )

        except asyncio.CancelledError:
            logger.warning(
                "Client connection cancelled: {}",
                client_address,
            )
            raise

        except OSError:
            logger.exception(
                "Socket error for {}",
                client_address,
            )

        except Exception:
            logger.exception(
                "Unhandled error for {}",
                client_address,
            )

        finally:
            writer.close()

            try:
                await writer.wait_closed()
            except OSError:
                pass

            async with self.active_clients_lock:
                self.active_clients -= 1
                current_clients = self.active_clients

            logger.info(
                "Client disconnected: {} | Active clients: {}",
                client_address,
                current_clients,
            )

    async def start_server(
        self,
        host: str = HOST,
        port: int = PORT,
    ) -> None:
        try:
            server = await asyncio.start_server(
                self.handle_client,
                host,
                port,
                backlog=BACKLOG,
                ssl=self.ssl_context,
            )

        except OSError:
            logger.exception(
                "Failed to start server on {}:{}",
                host,
                port,
            )
            raise

        addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])

        logger.success("Server listening on {}", addresses)
        logger.info("Waiting for clients")

        try:
            async with server:
                await server.serve_forever()

        except asyncio.CancelledError:
            logger.warning("Server shutting down")
            raise

        finally:
            server.close()
            await server.wait_closed()
            logger.info("Server socket closed")


def main() -> None:
    server = TCPServer()

    try:
        asyncio.run(server.start_server())

    except KeyboardInterrupt:
        logger.warning("Server stopped")

    except Exception:
        logger.exception("Fatal server error")


if __name__ == "__main__":
    main()
