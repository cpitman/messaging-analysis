from mq import capture
import CMQC
import unittest

queue_manager = "QM.1"
channel = "SVRCONN.1"
host = "localhost"
port = "1434"

queue_name = "TEST_QUEUE"
queue_type = CMQC.MQQT_LOCAL
queue_max_depth = "300"

class TestConnectionHandler(unittest.TestCase):

	def setUp(self):
		self.connection_handler = capture.ConnectionHandler(queue_manager, channel, host, port)
		self.connection_handler.connect()

	def test_create_and_delete_queue(self):
		self.connection_handler.create_queue(queue_name, queue_type, queue_max_depth)

		found = False
		queues = self.connection_handler.get_queues("*")
		for queue in queues:
			if queue[CMQC.MQCA_Q_NAME].strip() == queue_name:
				found = True
		self.assertTrue(found)

		self.connection_handler.delete_queue(queue_name)

		found = False
		queues = self.connection_handler.get_queues("*")
		for queue in queues:
			if queue[CMQC.MQCA_Q_NAME].strip() == queue_name:
				found = True
		self.assertTrue(found == False)

	def tearDown(self):
		self.connection_handler.disconnect()

if __name__ == '__main__':
	unittest.main()
	



