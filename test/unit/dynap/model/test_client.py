from unittest import TestCase

from dynap.model.client import Client


class TestClient(TestCase):

    def test_repr(self):
        client = Client(
            client_id="x",
            agent_address="localhost",
            topic="T-1",
            sink_address="localhost"
        )
        client_repr = client.to_repr()
        client_from_repr = Client.from_repr(client_repr)
        self.assertEqual(client, client_from_repr)
