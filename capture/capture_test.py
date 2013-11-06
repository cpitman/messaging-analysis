from mq import capture
import CMQC
import unittest

QUEUE_MANAGER = "QM.1"
CHANNEL = "SVRCONN.1"
HOST = "localhost"
PORT = "1434"

QUEUE_NAME = "TEST_QUEUE"
QUEUE_NAME2 = "TEST_QUEUE2"
QUEUE_NAME3 = "TEST_QUEUE3"
QUEUE_TYPE = CMQC.MQQT_LOCAL
QUEUE_MAX_DEPTH = "300"

TEST_MESSAGE = "TEST MESSAGE"
TEST_MESSAGE2 = "TEST MESSAGE 2"
TEST_MESSAGE3 = "TEST MESSAGE 3"

TEST_FILE = "test_file.json"

class TestCaptureStatistics(unittest.TestCase):

	def setUp(self):
		self.connection_handler = capture.ConnectionHandler(QUEUE_MANAGER, CHANNEL, HOST, PORT)
		self.connection_handler.connect()
		self.connection_handler.create_queue(QUEUE_NAME, QUEUE_TYPE, QUEUE_MAX_DEPTH)
		self.connection_handler.create_queue(QUEUE_NAME2, QUEUE_TYPE, QUEUE_MAX_DEPTH)
		self.connection_handler.create_queue(QUEUE_NAME3, QUEUE_TYPE, QUEUE_MAX_DEPTH)
		self.connection_handler.put_message_in_queue(QUEUE_NAME, TEST_MESSAGE)
		self.connection_handler.put_message_in_queue(QUEUE_NAME2, TEST_MESSAGE2)
		self.connection_handler.put_message_in_queue(QUEUE_NAME3, TEST_MESSAGE3)

	def test_capture_statistics(self):
		queue_statistics = capture.capture_statistics(self.connection_handler)
		capture.output_to_file(TEST_FILE, queue_statistics)

	def tearDown(self):
		self.connection_handler.delete_queue(QUEUE_NAME)
		self.connection_handler.delete_queue(QUEUE_NAME2)
		self.connection_handler.delete_queue(QUEUE_NAME3)
		self.connection_handler.disconnect()

class TestConnectionHandler(unittest.TestCase):

	def setUp(self):
		self.connection_handler = capture.ConnectionHandler(QUEUE_MANAGER, CHANNEL, HOST, PORT)
		self.connection_handler.connect()
		self.connection_handler.create_queue(QUEUE_NAME, QUEUE_TYPE, QUEUE_MAX_DEPTH)

	def test_browse_messages_in_queue(self):
		self.connection_handler.put_message_in_queue(QUEUE_NAME, TEST_MESSAGE)
		self.connection_handler.put_message_in_queue(QUEUE_NAME, TEST_MESSAGE2)
		self.connection_handler.put_message_in_queue(QUEUE_NAME, TEST_MESSAGE3)
		messages = self.connection_handler.browse_messages_in_queue(QUEUE_NAME)
		self.assertEqual(messages[0].body, TEST_MESSAGE)
		self.assertEqual(messages[1].body, TEST_MESSAGE2)
		self.assertEqual(messages[2].body, TEST_MESSAGE3)
		
	def test_get_queue_statistics(self):
		self.connection_handler.put_message_in_queue(QUEUE_NAME, TEST_MESSAGE)
		queue_statistics = self.connection_handler.get_queue_statistics(QUEUE_NAME)
		self.assertEqual(1, queue_statistics[CMQC.MQIA_CURRENT_Q_DEPTH])

	def test_put_and_get_message(self):
		self.connection_handler.put_message_in_queue(QUEUE_NAME, TEST_MESSAGE)
		message = self.connection_handler.get_message_in_queue(QUEUE_NAME)
		self.assertEqual(message, TEST_MESSAGE)

	def test_get_queues(self):
		found = False
		queues = self.connection_handler.get_all_queues()
		for queue in queues:
			if queue[CMQC.MQCA_Q_NAME].strip() == QUEUE_NAME:
				found = True
		self.assertTrue(found)

	def tearDown(self):
		self.connection_handler.delete_queue(QUEUE_NAME)
		self.connection_handler.disconnect()

if __name__ == '__main__':
	unittest.main()
	



