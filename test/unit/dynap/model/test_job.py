from unittest import TestCase

from dynap.model.job import Stream, Job, DeployedJob


class TestStream(TestCase):

    def test_repr(self):
        stream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        stream_repr = stream.to_repr()
        stream_from_repr = Stream.from_repr(stream_repr)
        self.assertEqual(stream, stream_from_repr)


class TestJob(TestCase):

    def test_repr(self):
        upstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        downstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        job = Job(
            job_name="A_job",
            agent_address="localhost",
            upstream=[upstream],
            downstream=[downstream],
            entry_class="test.package.class",
            sequence_number=1
        )
        job_repr = job.to_repr()
        job_from_repr = Job.from_repr(job_repr)
        self.assertEqual(job, job_from_repr)


class TestDeployedJob(TestCase):

    def test_repr(self):
        upstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        downstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        job = DeployedJob(
            job_name="A_job",
            agent_address="localhost",
            upstream=[upstream],
            downstream=[downstream],
            entry_class="test.package.class",
            jar_id="x",
            job_id="y",
            jar_name="test_jar_name",
            sequence_number=1,
            requesting_cs=False
        )
        job_repr = job.to_repr()
        job_from_repr = DeployedJob.from_repr(job_repr)
        self.assertEqual(job, job_from_repr)

    def test_print(self):
        upstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        downstream = Stream(
            address="localhost",
            topic="topic1",
            sequence_number=1,
            requesting_cs=False
        )
        job = DeployedJob(
            job_name="A_job",
            agent_address="localhost",
            upstream=[upstream],
            downstream=[downstream],
            entry_class="test.package.class",
            jar_id="x",
            job_id="y",
            jar_name="test_jar_name",
            sequence_number=1,
            requesting_cs=False
        )

        print(job.requesting_cs)

    def test_compare(self):
        string_a = "A_job"
        string_b = "2_job"

        print(string_a < string_b)
