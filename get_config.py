config = {}
config["serverLocation"] = "LCEC "
  
config["sendEmails"] = True   # send email when tolerance is exceeded or error occurs
#config["alertMaximum"] = 85   # max temperature (F) before alerting
#config["alertMinimum"] = 35    # min temperature (F) before alerting
config["alertHysteresis"] = 3  # how much recovery (beyond limit) do we need to clear alert (now using time)
config["maxTry"] = 1000       # number of tries before it gives up and sends an email
config["PLOT_INT"] = 5*60
config["SAMPLE_PERIOD"] = 60*1
config["recipient"] = "eric.howland@gmail.com"
config["log_rotate_days"] = 30
#config["web_path"] = "/var/www/"  # expects to have final /
config["web_path"] = "../www/"  # expects to have final /
# config[""] = 
  
