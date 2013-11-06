import argparse
import json
import pymqi
from time import time, sleep
import CMQC, CMQCFC, CMQXC

ALL_PREFIX = "*"

def parse_command_line_arguments():
	parser = argparse.ArgumentParser(description="Captures the message statistics for the provided queue manager.")

	#Positional required arguments
	parser.add_argument("queue_manager", help="The name of the queue manager")
	parser.add_argument("interval", type=int, help="The number of seconds between each capture")

	#Optional arguments
	parser.add_argument("-a", "--address", default="localhost", help="The host that the queue manager is located at")
	parser.add_argument("-c", "--channel", default="SVRCONN.1", help="The channel to use to connect to the queue manager")
	parser.add_argument("-f", "--file", default="statistics_output", help="The path to write the captured statistics to") 
	parser.add_argument("-p", "--port", default=1434, help="The port to connect to")
	parser.add_argument("-r", "--runs", type=int, help="The number of times to run the capture. This may not be used with the time option.")
	parser.add_argument("-t", "--time", type=int, help="Amount of time to run the capture in seconds. This may not be used with the runs option.")

	args = parser.parse_args()

	if args.runs and args.time:
		raise RuntimeError, "The arguments -r/--runs and -t/--time cannot both be specified"    
	if not args.runs and not args.time:
		raise RuntimeError, "The argument -r/--runs or -t/--time is required"

	return args

def capture_statistics(connection_handler):
	queues = connection_handler.get_all_queues()
	queue_statistics = []
	for queue in queues:
		queue_name = queue[CMQC.MQCA_Q_NAME]
		try:
			messages = connection_handler.browse_messages_in_queue(queue_name)
			statistics = connection_handler.get_queue_statistics(queue_name)
			queue_statistics.append(QueueStatistics(queue_name, messages, statistics))
		except pymqi.MQMIError, e:
			print "Failed to read queue '%s'" % queue_name.split() 

	return queue_statistics
	
def output_to_file(filename, queue_statistics):
		f = open(filename, "a")
		f.write(json.dumps(Captures(queue_statistics).__dict__))
		f.close()
	
#Class to handle the connection to the Websphere MQ broker
class ConnectionHandler:

	def __init__(self, queue_manager, channel, host, port):
		self.queue_manager = queue_manager
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
		self.connection.connect_with_options(self.queue_manager, cd=self.cd, opts=CMQC.MQCNO_HANDLE_SHARE_BLOCK)
		
	def create_queue(self, queue_name, queue_type, max_depth):
		args = {CMQC.MQCA_Q_NAME: queue_name, CMQC.MQIA_Q_TYPE: queue_type, CMQC.MQIA_MAX_Q_DEPTH: max_depth}
		try:
			self.connection.MQCMD_CREATE_Q(args)
		except pymqi.MQMIError, e:
			if e.reason == CMQCFC.MQRCCF_OBJECT_ALREADY_EXISTS:
				print "Warning: Queue '%s' already exists on queue manager '%s'!" % (queue_name, self.queue_manager)
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
				print "The queue '%s' was not found." % queue_name.strip()
			else:
				raise

		return response[0]

	def get_all_queues(self):
		args = {CMQC.MQCA_Q_NAME: ALL_PREFIX, CMQC.MQIA_Q_TYPE: CMQC.MQQT_LOCAL}
		return self.connection.MQCMD_INQUIRE_Q(args)

	def put_message_in_queue(self, queue_name, message):
		queue = pymqi.Queue(self.connection, queue_name)
		queue.put(message)
		queue.close()

class Message:
		
	def __init__(self, header, body):
		self.header = header
		self.body = body
		self.parse_header()

	def parse_header(self):
		self.size = len(self.body)
		if self.header['Persistence'] == 1:
			self.persistent = True
		else:
			self.persistent = False

#Json parseable class holding the overall statistics
class Captures:

	def __init__(self, queue_statistics):
		self.time = time()
		self.captures = []
		for statistic in queue_statistics:
			self.captures.append("%s" % json.dumps(statistic.__dict__))

#Json parseable class holding the queue statistics
class QueueStatistics:

	def __init__(self, queue_name, messages, statistics):
		self.queueName = queue_name.split()[0]
		self.depth = statistics[CMQC.MQIA_CURRENT_Q_DEPTH]
		self.msgIn = statistics[CMQC.MQIA_OPEN_INPUT_COUNT]
		self.msgOut = statistics[CMQC.MQIA_OPEN_OUTPUT_COUNT]
		
		self.msgs = []
		for message in messages:
			self.msgs.append(["size:%s" % message.size, "persistent:%s" % message.persistent])
		
if __name__ == '__main__':
	args = parse_command_line_arguments()

	connection_handler = ConnectionHandler(args.queue_manager, args.channel, args.address, args.port)
	connection_handler.connect()

	if args.runs:
		times = 0
		while times < args.runs:
			queue_statistics = capture_statistics(connection_handler)
			output_to_file(filename, queue_statistics)
			times += 1
			sleep(args.interval)
	else:
		end_time = time() + args.time
		while time() < end_time:
			queue_statistics = capture_statistics(connection_handler)
			output_to_file(filename, queue_statistics)
			time.sleep(args.interval)

	
	

