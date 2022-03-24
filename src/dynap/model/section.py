from __future__ import absolute_import, annotations
from dataclasses import dataclass

import logging
logger = logging.getLogger("dynap.model.section")


@dataclass
class CriticalSection:
    job_name: str
    agent_address: str
    sequence_number: int
    topic: str

    def to_repr(self) -> dict:
        return {
            "job_name": self.job_name,
            "topic": self.topic,
            "sequence_number": self.sequence_number,
            "agent_address": self.agent_address
        }

    @staticmethod
    def from_repr(raw_data: dict) -> CriticalSection:
        return CriticalSection(
            job_name=raw_data["job_name"],
            topic=raw_data["topic"],
            sequence_number=raw_data["sequence_number"],
            agent_address=raw_data["agent_address"]
        )
