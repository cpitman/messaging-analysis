import pymqi
import CMQC, CMQCFC, CMQXC

#Class to handle the connection to the Websphere MQ broker
class ConnectionHandler:

	def __init__(self, queue_manager, channel, host, port):
		self.__queue_manager = queue_manager
		self.cd = pymqi.CD()
		self.cd.ChannelName = channel
		self.cd.ConnectionName = "%s(%s)" % (host, port)
		self.cd.ChannelType = CMQC.MQCHT_CLNTCONN
		self.cd.TransportType = CMQC.MQXPT_TCP

	def browse_messages_in_queue(self, queue_name):
		queue = pymqi.Queue(self.connection, queue_name, CMQC.MQOO_BROWSE)

		message_descriptors = pymqi.md()
		get_message_options = pymqi.gmo()
		get_message_options.Options = CMQC.MQGMO_BROWSE_NEXT

		messages = []
		while True:
			try:
				message_body = queue.get(None, message_descriptors, get_message_options)
				messages.append(Message(message_descriptors, message_body))

				#These are required in order to move the cursor to the next entry.
				message_descriptors['MsgId'] = ''
				message_descriptors['CorrelId'] = ''
			except pymqi.MQMIError, e:
				if e.comp == CMQC.MQCC_FAILED and e.reason == CMQC.MQRC_NO_MSG_AVAILABLE:
					break
				else:
					raise

		queue.close()

		return messages
		
	def connect(self):
		self.connection = pymqi.PCFExecute(name = None)
		self.connection.connect_with_options(self.__queue_manager, cd=self.cd, opts=CMQC.MQCNO_HANDLE_SHARE_BLOCK)
		
	def create_queue(self, queue_name, queue_type, max_depth):
		args = {CMQC.MQCA_Q_NAME: queue_name, CMQC.MQIA_Q_TYPE: queue_type, CMQC.MQIA_MAX_Q_DEPTH: max_depth}
		try:
			self.connection.MQCMD_CREATE_Q(args)
		except pymqi.MQMIError, e:
			if e.reason == CMQCFC.MQRCCF_OBJECT_ALREADY_EXISTS:
				print "Warning: Queue '%s' already exists on queue manager '%s'!" % (queue_name, self.__queue_manager)
			else:
				raise

	def delete_queue(self, queue_name):
		args = {CMQC.MQCA_Q_NAME: queue_name}
		self.drain_queue(queue_name)
		self.connection.MQCMD_DELETE_Q(args)

	def disconnect(self):
		self.connection.disconnect()

	def drain_queue(self, queue_name):
		queue = pymqi.Queue(self.connection, queue_name)

		while True:
			try:
				queue.get()
			except pymqi.MQMIError, e:
				if e.comp == CMQC.MQCC_FAILED and e.reason == CMQC.MQRC_NO_MSG_AVAILABLE:
					break
				else:
					raise
		
		queue.close()
	
	def get_message_in_queue(self, queue_name):
		queue = pymqi.Queue(self.connection, queue_name)
		message = queue.get()
		queue.close()
		return message

	def get_queue_statistics(self, queue_name):
		args = {CMQC.MQCA_Q_NAME: queue_name, CMQCFC.MQIACF_Q_STATUS_TYPE: CMQCFC.MQIACF_Q_STATUS}

		try:
			response = self.connection.MQCMD_INQUIRE_Q_STATUS(args)
		except pymqi.MQMIError, e:
			if e.comp == CMQC.MQCC_FAILED and e.reason== CMQC.MQRC_UNKNOWN_OBJECT_NAME:
				print "The queue '%s' was not found." % queue_name
			else:
				raise

		return response[0]

	def get_queues(self, inquiry):
		args = {CMQC.MQCA_Q_NAME: inquiry}
		return self.connection.MQCMD_INQUIRE_Q(args)

	def put_message_in_queue(self, queue_name, message):
		queue = pymqi.Queue(self.connection, queue_name)
		queue.put(message)
		queue.close()

class Message:
		
	def __init__(self, header, body):
		self.header = header
		self.body = body


