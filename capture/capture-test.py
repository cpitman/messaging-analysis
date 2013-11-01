# This is pulled from the example code on pythonhosted.org/pymqi/examples.html

import pymqi

queue_manager = "QM.1"
channel = "SVRCONN.1"
host = "localhost"
port = "1434"
conn_info = "%s(%s)" % (host, port)
message = "SUCCESS!"

qmgr = pymqi.connect(queue_manager, channel, conn_info)

print "SUCCESS!"
qmgr.disconnect()
