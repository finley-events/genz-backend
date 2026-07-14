import json
import threading
import time
from typing import Any

from websocket import WebSocket, create_connection


class DerivWebSocketService:
    """
    Low-level WebSocket client for the Deriv Options API.

    This class is only responsible for maintaining a WebSocket
    connection. Authentication is handled beforehand by obtaining
    a one-time WebSocket URL through the OTP endpoint.
    """

    def __init__(
        self,
        websocket_url: str,
        timeout: int = 30,
        heartbeat_interval: int = 25,
    ):
        self.websocket_url = websocket_url
        self.timeout = timeout
        self.heartbeat_interval = heartbeat_interval

        self.ws: WebSocket | None = None
        self.connected = False

        self._heartbeat_thread = None
        self._stop_heartbeat = False

    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------

    def connect(self):
        """
        Establish a WebSocket connection.
        """

        if self.connected:
            return

        self.ws = create_connection(
            self.websocket_url,
            timeout=self.timeout,
        )

        self.connected = True

        self._start_heartbeat()

    def disconnect(self):
        """
        Close the WebSocket connection.
        """

        self._stop_heartbeat = True

        if self.ws:

            try:
                self.ws.close()
            finally:
                self.ws = None

        self.connected = False

    # --------------------------------------------------
    # SEND / RECEIVE
    # --------------------------------------------------

    def send(self, payload: dict[str, Any]):
        """
        Send a JSON payload.
        """

        if not self.connected or self.ws is None:
            raise RuntimeError("WebSocket is not connected.")

        self.ws.send(json.dumps(payload))

    def receive(self) -> dict[str, Any]:
        """
        Receive the next JSON message.
        """

        if not self.connected or self.ws is None:
            raise RuntimeError("WebSocket is not connected.")

        message = self.ws.recv()

        return json.loads(message)

    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send a request and wait for a single response.
        """

        self.send(payload)

        return self.receive()

    # --------------------------------------------------
    # HEARTBEAT
    # --------------------------------------------------

    def _heartbeat(self):
        """
        Keeps the WebSocket alive.
        """

        while not self._stop_heartbeat:

            try:
                if self.connected and self.ws is not None:
                    self.ws.ping()

            except Exception:
                break

            time.sleep(self.heartbeat_interval)

            time.sleep(self.heartbeat_interval)

    def _start_heartbeat(self):

        self._stop_heartbeat = False

        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat,
            daemon=True,
        )

        self._heartbeat_thread.start()

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    @property
    def is_connected(self):

        return self.connected
