from __future__ import absolute_import, annotations
from dataclasses import dataclass

import logging

logger = logging.getLogger("dynap.model")


@dataclass
class Client:
    client_id: str
    agent_address: str
    topic: str
    sink_address: str

    def to_repr(self) -> dict:
        return {
            "client_id": self.client_id,
            "agent_address": self.agent_address,
            "topic": self.topic,
            "sink_address": self.sink_address
        }

    @staticmethod
    def from_repr(raw_data: dict) -> Client:
        return Client(
            client_id=raw_data["client_id"],
            agent_address=raw_data["agent_address"],
            topic=raw_data["topic"],
            sink_address=raw_data["sink_address"]
        )

    @staticmethod
    def build_name(topic: str) -> str:
        return f"{topic}_forwarder"

