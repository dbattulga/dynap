from __future__ import absolute_import, annotations
from dataclasses import dataclass

import logging
logger = logging.getLogger("dynap.model.section")


@dataclass
class UpdateStream:
    agent_address: str
    topic: str

    def to_repr(self) -> dict:
        return {
            "topic": self.topic,
            "agent_address": self.agent_address
        }

    @staticmethod
    def from_repr(raw_data: dict) -> UpdateStream:
        return UpdateStream(
            topic=raw_data["topic"],
            agent_address=raw_data["agent_address"]
        )
