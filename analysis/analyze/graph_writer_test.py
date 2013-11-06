import unittest
import digester
import shutil
import graph_writer
import os
import numpy.random as nprnd
import tempfile

STATS = {'overallStats': {'maxMsgSize': 3560, 'allDepths':[8, 22, 35], 'allMsgSizes': [  30,   26,   18,   22,   20,   18,  400,   92,  200,  600,   18, 14,  100,  299, 3560,   20,   18,  400], 'avgDepth': 6.0, 'avgMsgInRate': 9.0, 'avgMsgOutRate': 9.0, 'stdDevMsgSize': 802.81849377715321, 'minMsgSize': 14}, 'intervalStats': [{'msgInRate': 13.0, 'endTime': 3000, 'startTime': 2000, 'msgOutRate': 13.0}, {'msgInRate': 5.0, 'endTime': 4000, 'startTime': 3000, 'msgOutRate': 5.0}]}

CLEANUP = True

class TestGraphWriter(unittest.TestCase):

	def setUp(self):
		self.graph_writer = graph_writer.GraphWriter()

	def test_show_graphs(self):
		tmp_dir = tempfile.mkdtemp()
		self.graph_writer.create_graphs(STATS, tmp_dir)
		if CLEANUP: shutil.rmtree(tmp_dir)

	def test_create_size_hist(self):

		tmp_dir = tempfile.mkdtemp()
		self.graph_writer.create_msg_size_histogram({'overallStats':{'allMsgSizes': nprnd.random_integers(1, 1000, 2000)}}, tmp_dir)
		print "Msg size histogram is "+ os.path.join(tmp_dir,"msg_size_hist.jpeg")
		if CLEANUP: shutil.rmtree(tmp_dir)

	def test_create_msg_depth_hist(self):
		tmp_dir = tempfile.mkdtemp()
		random_ints = nprnd.random_integers(1, 1000, 2000)
		stats = {'overallStats': {'allDepths': random_ints}}

		self.graph_writer.create_msg_depth_histogram(stats, tmp_dir)
		print "Msg depth histogram is "+ os.path.join(tmp_dir,"msg_depth_hist.jpeg")
		if CLEANUP: shutil.rmtree(tmp_dir)

	def test_pdf_writer(self):
		tmp_dir = tempfile.mkdtemp()
		self.graph_writer.create_graphs(STATS, tmp_dir)
		print "PDF filename is " + os.path.join(tmp_dir, "report.pdf")
		self.graph_writer.write_pdf(tmp_dir)
		if CLEANUP: shutil.rmtree(tmp_dir)

if __name__ == '__main__':
  unittest.main()
