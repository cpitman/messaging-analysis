import json
import numpy
import os
class Digester:

	def load_json(self, json_str):
		json_obj = json.loads(json_str)
		queue_name = json_obj["queueName"]
  
	def process_statistics(self, stats):
		processed_stats = {"intervalStats":[], "captureStats":[], "overallStats":{}}
		stats = sorted(stats, key=lambda stat: stat["time"])

		if(len(stats) > 1):
			for i in range(1, len(stats)):
				interval = {}
				interval["msgInRate"] = float(stats[i]["msgIn"] - stats[i-1]["msgIn"]) / float((stats[i]["time"] - stats[i-1]["time"]) / 1000)
				interval["msgOutRate"] = float(stats[i]["msgIn"] - stats[i-1]["msgIn"]) / float((stats[i]["time"] - stats[i-1]["time"]) / 1000)
				interval["startTime"] = stats[i-1]["time"]
				interval["endTime"] = stats[i]["time"]

				processed_stats["intervalStats"].append(interval)

			msg_sizes = []
			for i in range(0, len(stats)):
				capture = {}
				capture["avgMessageSize"] = numpy.average(numpy.array(stats[i]["msgSizes"]))
				capture["msgDepth"] = stats[i]["depth"]
				capture["time"] = stats[i]["time"]
				processed_stats["captureStats"].append(capture)
				msg_sizes.append(stats[i]["msgSizes"])
			
			msg_sizes = numpy.array([item for sublist in msg_sizes for item in sublist])
			processed_stats["overallStats"]["avgDepth"] = numpy.average(numpy.array([ stat["depth"] for stat in stats ]))
			processed_stats["overallStats"]["avgMsgInRate"] = numpy.average(numpy.array([ stat["msgInRate"] for stat in processed_stats["intervalStats"] ]))
			processed_stats["overallStats"]["avgMsgOutRate"] = numpy.average(numpy.array([ stat["msgOutRate"] for stat in processed_stats["intervalStats"] ]))
			processed_stats["overallStats"]["maxMsgSize"] = numpy.max(msg_sizes)
			processed_stats["overallStats"]["minMsgSize"] = numpy.min(msg_sizes)
			processed_stats["overallStats"]["stdDevMsgSize"] = numpy.std(msg_sizes)
			processed_stats["overallStats"]["allMsgSizes"] = msg_sizes

			print processed_stats
		else:
			raise ValueError("Not enough stats to extrapolate results")

		return processed_stats
