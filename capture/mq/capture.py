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

	def connect(self):
		self.connection = pymqi.QueueManager(None)
		self.connection.connect_with_options(self.__queue_manager, cd=self.cd, opts=CMQC.MQCNO_HANDLE_SHARE_BLOCK)
		self.programmable_command_format = pymqi.PCFExecute(self.__queue_manager)

	def create_queue(self, queue_name, queue_type, max_depth):
		args = {CMQC.MQCA_Q_NAME: queue_name, CMQC.MQIA_Q_TYPE: queue_type, CMQC.MQIA_MAX_Q_DEPTH: max_depth}
		self.programmable_command_format.MQCMD_CREATE_Q(args)

	def delete_queue(self, queue_name):
		args = {CMQC.MQCA_Q_NAME: queue_name}
		self.programmable_command_format.MQCMD_DELETE_Q(args)

	def disconnect(self):
		self.connection.disconnect()

	def get_queues(self, inquiry):
		args = {CMQC.MQCA_Q_NAME: inquiry}
		return self.programmable_command_format.MQCMD_INQUIRE_Q(args)

#Class that utilizes the connection handler
class StatisticsGatherer:

	def __init__(self, connection_handler):
		self.__connection_handler = connection_handler

	def get_queue_statistics(self, queue_name):
		args = {CMQC.MQCA_Q_NAME: queue_name, CMQCFC.MQIACF_Q_STATUS_TYPE: CMQCFC.MQIACF_Q_STATUS, CMQCFC.MQIACF_Q_STATUS_ATTRS: CMQC.MQIA_CURRENT_Q_DEPTH}

		try:
			response = self.__connection_handler.programmable_command_format.MQCMD_INQUIRE_Q_STATUS(args)
		except pymqi.MQMIError, e:
			if e.comp == CMQC.MQCC_FAILED and e.reason== CMQC.MQRC_UNKNOWN_OBJECT_NAME:
				print "No queues matched given arguments."
			else:
				raise

		for queue_info in response:
			queue_name = queue_info[CMQC.MQCA_Q_NAME]
			print "Found queue [%s]" % queue_name
