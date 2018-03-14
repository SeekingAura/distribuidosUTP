import time
import ntplib
t = (2018, 3, 11, 19, 3, 38, 1, 48, 0)
c = ntplib.NTPClient()
response = c.request('time4.google.com', version=3) 
secs = response.tx_time
print("de ntp", response.tx_time)
print("de time clock", time.clock())
for i in range(10):
    print ("time.mktime(t) : ", secs)
    tempTime=time.asctime(time.localtime(secs+time.clock()))
    print ("asctime(localtime(secs)): %s" % tempTime[0:4]+tempTime[8:10]+"/"+tempTime[4:6]+"/"+tempTime[20:24], tempTime[11:19])
    time.sleep(1)