from unittest import TestCase

from dynap.model.job import Stream, Job, DeployedJob


class TestStream(TestCase):

    def test_repr(self):
        stream = Stream(
            address="localhost",
            topic="topic1"
        )
        stream_repr = stream.to_repr()
        stream_from_repr = Stream.from_repr(stream_repr)
        self.assertEqual(stream, stream_from_repr)


class TestJob(TestCase):

    def test_repr(self):
        upstream = Stream(
            address="localhost",
            topic="topic1"
        )
        downstream = Stream(
            address="localhost",
            topic="topic1"
        )
        job = Job(
            job_name="A_job",
            agent_address="localhost",
            upstream=[upstream],
            downstream=[downstream],
            entry_class="test.package.class"
        )
        job_repr = job.to_repr()
        job_from_repr = Job.from_repr(job_repr)
        self.assertEqual(job, job_from_repr)


class TestDeployedJob(TestCase):

    def test_repr(self):
        upstream = Stream(
            address="localhost",
            topic="topic1"
        )
        downstream = Stream(
            address="localhost",
            topic="topic1"
        )
        job = DeployedJob(
            job_name="A_job",
            agent_address="localhost",
            upstream=[upstream],
            downstream=[downstream],
            entry_class="test.package.class",
            jar_id="x",
            job_id="y",
            jar_name="test_jar_name"
        )
        job_repr = job.to_repr()
        job_from_repr = DeployedJob.from_repr(job_repr)
        self.assertEqual(job, job_from_repr)
