import unittest
import digester
import shutil

class TestDigester(unittest.TestCase):

	def setUp(self):
		self.digester = digester.Digester()

	def test_json_digest(self):
		self.digester.load_json('{"queueName":"testQueue", "statistics":[ { } ]}')

	def test_process_stats_1_stat(self):
		self.assertRaises(ValueError, self.digester.process_statistics, [{"msgIn":5, "msgOut":2, "depth":3, "time":"testTime"}])

	def test_process_stats(self):
		stats = self.digester.process_statistics([{"msgIn":30, "msgOut":27, "depth":3, "time":4000, "msgSizes":[20,18,400]}, {"msgIn":12, "msgOut":8, "depth":4, "time":2000, "msgSizes":[30,26,18,22]}, {"msgIn":25, "msgOut":12, "depth":11, "time":3000, "msgSizes":[20,18,400,92,200,600,18,14,100,299,3560]} ])
		self.assertEqual(6, stats["overallStats"]["avgDepth"])
		self.assertEqual(3, len(stats["captureStats"]))
		self.assertEqual(2, len(stats["intervalStats"]))

if __name__ == '__main__':
  unittest.main()
