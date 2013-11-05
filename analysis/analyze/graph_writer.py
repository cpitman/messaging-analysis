from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
import os
import tempfile
import matplotlib.pyplot as plt

class GraphWriter:

	def write_pdf(self, file_loc):
		c = canvas.Canvas(os.path.join(file_loc,'report.pdf'))
		images = os.listdir(file_loc)
		for image in images:
			c.drawImage(os.path.join(file_loc,image), 0, 0, 20*cm, 15*cm)
			c.showPage()

		c.save()


	def create_graphs(self, stats, test=False):
		tmpdir = tempfile.mkdtemp()
		print tmpdir

		bar_width = (stats["captureStats"][1]["time"] - stats["captureStats"][0]["time"]) / 10
		x,y = [], []
		for i in range(0,len(stats["captureStats"])):
			x.append(stats["captureStats"][i]["time"])
			y.append(stats["captureStats"][i]["msgDepth"])
			
		plt.bar(x,y,width=bar_width)
		plt.xlabel('Time')
		plt.ylabel('Msg Depth')
		plt.title('Msg Depth Over Time')
		plt.grid(True)
		plt.draw()
		plt.savefig(os.path.join(tmpdir,"msg_depth.jpeg"))

		bar_width = (stats["intervalStats"][0]["startTime"] - stats["intervalStats"][0]["endTime"]) / 10
		x,y = [], []
		for i in range(0,len(stats["intervalStats"])):
			x.append(stats["intervalStats"][i]["startTime"])
			y.append(stats["intervalStats"][i]["msgInRate"])
			
		plt.figure()
		plt.bar(x,y,width=bar_width)
		plt.xlabel('Start Time')
		plt.ylabel('Msg Rate (msgs/second)')
		plt.title('Msg In Rate Over Time')
		plt.grid(True)
		plt.draw()
		plt.savefig(os.path.join(tmpdir,"msg_in_rate.jpeg"))

		if(test):
			plt.show()

		return tmpdir

