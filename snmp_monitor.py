from __future__ import print_function
# this file is adapted from http://jartweb.net/blog/wp-content/uploads/2013/12/Raspberry-Pi-Logger-with-LCD.pdf

import os, os.path, glob, time, sys, datetime, smtplib
global device_file


# define some globals
ONEDAY = 24*60*60


from .getcmd_snmp import *
from .plot_temp_date import *
from .display_LCD import *

from . import send_email 
from . import get_config



#####config_dict = get_config.get_config()
## see:  https://docs.python.org/2/faq/programming.html?highlight=global%20variables#how-do-i-share-global-variables-across-modules

device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = device_folder[0] + '/w1_slave'

def get_reading(device_file):
    
    return reading_c, reading_f

def daily():
  days = get_config.config["log_rotate_days"]
  filepath = get_config.config["web_path"]
  print (days, filepath)
  readings = glob.glob(os.path.join(filepath, "readings*"))
  plots = glob.glob(os.path.join(filepath, "plot*"))
  
  readings.sort(reverse=True)
  plots.sort(reverse=True)
  #print ("pre", readings, plots)
  readings = readings[days:]
  plots = plots[days:]  
  #print ("post truncate",readings, plots)
  
  for plot in plots: 
    os.remove(plot)
  for readings_file in readings:
    os.remove(readings_file)

  
def get_statistics(readings):
  readings.sort()
  min = readings[0]
  max = readings[-1]
  median = readings[int(len(readings)/2)]
  return min, max, median
    

def check_4_alert(reading_in_f ): #This is an iterator so dates preserve between constants
    #global readings_f # [remove this is kludge maybe should be a class]
    last_alert = datetime.datetime.today()-datetime.timedelta(days=1).timestamp()
        ## start more than one day ago
    print ("ChecK_alter info", reading_in_f)
    for dat in reading_in_f:
        print("Check_4_alert_info loop: ", dat, last_alert)
        today = datetime.datetime.today().timestamp()
        error_str = ""  ## clear each time through loop

        if (dat == -999):
            if(today - last_alert) > ONEDAY:
                error_str = "sensor error"

        elif (dat < alertMinimum):
            if(today - last_alert) > ONEDAY:
                error_str = "low temperature alert %6.1f F"%reading_in_f

        elif (dat > alertMaximum):
             if(today - last_alert) > ONEDAY:
                error_str='high temperature alert %6.1f F"%reading_in_f'
                    
        else: ## Server is OK
            print('T1:'+str(dat))
            continue  ## get a new data point
            

        error_subject = "ERROR from server %s %s at %s"% (serverLocation,
                                                         error_str,
                                                         serverLocation+now.strftime(" %Y-%m-%dT%H:%M:%S"),)
        #error_body =  ("""\n\nMin Temp was: %6.2f F
        #                Max Temp was: %6.2f F\n
        #                Median Temp was: %6.2f F \n"""%
        #                get_statistics(readings_f))  ## min, max, median

        error_body = "Temperature is: %6.1f"% reading_in_f                                                   
        send_email.sendMail(error_subject,
             now.strftime("%Y-%m-%dT%H:%M:%S")+error_body,
             attachmentFilePaths)
       
        yield dat  # this makes this function an iterator



######################################
# this is the top of the real program with setup
######################################

device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = device_folder[0] + '/w1_slave'
##remove lcd = LCD.Adafruit_CharLCDPlate()

print ("monitor_server: device_file",device_file)




last_housekeeping = time.time() - ONEDAY  #force first pass to trigger
last_plot = time.time() - ONEDAY  #force first pass to trigger by setting lat plot to one day ago"

yesterday = datetime.datetime.today()-datetime.timedelta(days=1)
last_day = yesterday.strftime("%Y-%m-%d")
last_clearance  = datetime.datetime.today()

today_str=time.strftime("%Y-%m-%d", time.localtime())
text_outfilename="/var/www/readings"+today_str+".csv"
last_plot_name = "/var/www/plot"+today_str+".png"


time.sleep(10)

readings_f = []
dates = []
OUTFILE = False

###########################################
#This is the main loop which cycles forever
###########################################

while 1:
    if not(OUTFILE) or not(os.path.isfile(text_outfilename)):
        OUTFILE = open(text_outfilename, "a") # lets append rather than truncate if it already exists
    
    reading_c, reading_f = get_reading(device_file)
    readings_f.append(reading_f)
    dates.append(datetime.datetime.today())
    
    output_str = "%s, %6.1f, %6.1f\n"%(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                                           reading_f, reading_c)
   
 
    print (output_str)
    OUTFILE.write(output_str)
    #OUTFILE.flush()

    display_time=time.strftime("%Y-%m-%d %I:%M %p", time.localtime())
    display_LCD(display_time, reading_c, reading_f)
    
    
    today_str=time.strftime("%Y-%m-%d", time.localtime())
    
    
    print ("today_str:", today_str)
    print ("last_day: ", last_day)


    #### At the end of the day reset things
    if (today_str > last_day):
        # daily tasks - Do this when day changes.
        #attachmentFilePaths = [last_plot_name, text_outfilename ]
        if os.path.isfile(last_plot_name):       # do not try to attach  if it does not exist
          attachmentFilePaths = [last_plot_name] # raw csv data getting encoded
        else:
          attachmentFilePaths = []
        last_clearance = now = datetime.datetime.today()

	(mint, maxt, mediant) = get_statistics(readings_f)
        message_subject = "Update from server %s"% get_config.config["serverLocation"]+now.strftime("%Y-%m-%dT%H:%M:%S")
	message_subject = message_subject + " Max Temp %6.2f F"%maxt
        message_body = """\n\nMin Temp was: %6.1f F
Max Temp was: %6.1f F
Median Temp was: %6.1f F """%(mint, maxt, mediant)
        send_email.sendMail(message_subject,
             now.strftime("%Y-%m-%dT%H:%M:%S")+message_body,
             attachmentFilePaths)

        
        readings_f=readings_f[0:0]
        dates = dates[0:0]
        last_day = today_str
        last_housekeeping = time.time()
        OUTFILE.close()
        
        text_outfilename="/var/www/readings"+time.strftime("%Y-%m-%d", time.localtime())+".csv"
        OUTFILE = open(text_outfilename, "a") # again append if exists
        today_str=time.strftime("%Y-%m-%d", time.localtime())

        daily()


       ##### Do a plot every so often    
    if (time.time() - last_plot) > get_config.config["PLOT_INT"]:
    	OUTFILE.flush() # strike a balance between every write and waiting f
			#for the buffer to fill - more than half a day
 
        #do not putout an empty graph at the start of the day
#  -------  Change so if plot has less than 2 readings just does not plot
#
#        while len(readings_f) < 2:  ## get 2 readings for at least some kind of graph.
#            time.sleep(get_config.config["SAMPLE_PERIOD"])
#            reading_c, reading_f = get_reading(device_file)
#            readings_f.append(reading_f)
#            dates.append(datetime.datetime.today())
            

        last_plot_name = "/var/www/plot"+today_str+".png"
        plotdata(dates, readings_f, text_outfilename, last_plot_name)
        last_plot = time.time()
        #overwrites all day then goes on to new day

   
    temp = check_4_alert(reading_f)# check and potentialy send email after plot
      
    
    time.sleep(get_config.config["SAMPLE_PERIOD"])

