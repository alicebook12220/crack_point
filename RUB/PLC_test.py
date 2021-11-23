import gc
import time
import traceback
import pymcprotocol

LAB_USED=0
PLC_FAIL=0
LL_ALWAYS_OPEN=0

device = None
in_sensor = None
out_sensor = None
exist_glass = None
def plc_connect():
	global device
	while True:
		try:
			device = pymcprotocol.Type3E(plctype="QnA")
			device.setaccessopt(commtype="binary") #binary, ascii
			device.connect("192.168.0.100", 1025)
			print('PLC連線成功')
			break
		except:
			pass

def plc_read():
	global device
	global in_sensor
	global out_sensor
	global exist_glass
	try:
		if device is not None:
			in_sensor = device.batchread_bitunits(headdevice="X21", readsize=1)[0] #batchread_wordunits
			out_sensor = device.batchread_bitunits(headdevice="X20", readsize=1)[0]
			exist_glass = device.batchread_bitunits(headdevice="X20", readsize=1)[0]
	except:
		print('連線中斷，PLC嘗試重新連線')
		device = None
		plc_connect()
