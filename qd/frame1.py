####################################################################################################
#
# PROGRAM: frame1.py
# AUTHOR:  Alex Beyk abeyk@apixio.com
# DATE:    2014.07.20
#
#####################################################################################################

# LIBRARIES ####################################################################################################

import datetime
from datetime import datetime
from datetime import tzinfo
from datetime import timedelta
import logging
import os
import re
import sched
import smtplib
import socket
import sys
import time
from time import gmtime, strftime

# GLOBALS ####################################################################################################

gsVersion                  = "1.0"
gsAbout                    = "is a program for creating the Quality Dashboard frame1.html"
gsProgram                  = "".join(sys.argv[0])
gsLogFile                  = gsProgram + ".log.txt"
gsFrameFile                = "frame1.html"
gsGray                     = "#CCCCCC" # Title
gsGreen                    = "#00FF00" # Healthy
gsYellow                   = "#FFFF00" # UnHealthy
gsRed                      = "#FF0000" # Critical
gsWhite                    = "#FFFFFF" # Unknown
gsRunFrequency             = "1" # *AB* 1 = run every minute, 2 = run every 2 minutes, etc.
gsServerType               = "hccstage.apixio.com"
gsOverallStatus            = gsGreen # gsGreen = Healthy, gsYellow = Unhealthy, gsRed = Critical, gsWhite = Unknown
fhHtml                     = 0

# Set Up Python Logging
fLog = logging.getLogger(__name__)
fLog.setLevel(logging.INFO)
lHandler = logging.FileHandler(gsLogFile)
lFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
lHandler.setFormatter(lFormatter)
fLog.addHandler(lHandler)

# MAIN PROGRAM ####################################################################################################

def fRunMainProgram():
  fLog.info("Start " + gsProgram)
  fRunScheduler()
  fLog.info("Exit 0 " + gsProgram)
  exit(0)

# CLASSES ####################################################################################################

class Zone(tzinfo):
  def __init__(self,offset,isdst,name):
    self.offset = offset
    self.isdst = isdst
    self.name = name
  def utcoffset(self, dt):
    return timedelta(hours=self.offset) + self.dst(dt)
  def dst(self, dt):
    return timedelta(hours=1) if self.isdst else timedelta(0)
  def tzname(self,dt):
    return self.name

# FUNCTIONS ####################################################################################################

def fRunScheduler(): ####################################################################################################
  fLog.info("fRunScheduler")
  fLog.info("Running every " + gsRunFrequency + " minute(s)")
  print strftime("%Y-%m-%d %H:%M:%S") + " Running every " + gsRunFrequency + " minute(s)"
  while 1 == 1:
    liTimeSeconds = int(str(datetime.now()).split(':')[2][:2])
    if liTimeSeconds == 0: # Sleep until the seconds are 0, then run the tests
      fCreateFrame()
      time.sleep(int(gsRunFrequency) * 30)
    time.sleep(1)
  return 0

def fCreateFrame(): ####################################################################################################
  fLog.info("fCreateFrame")
  liAlertYellow = 0
  liAlertRed    = 0
  print strftime("%Y-%m-%d %H:%M:%S") + " Starting to Create " + gsFrameFile
  fLog.info("Started Creating " + gsFrameFile)
  fhHtml = open(gsFrameFile, "w")


# *AB* *AB*

#  fRun = os.popen("hostname")
#  lsTestResult = fRun.read()
#  liAlertYellow = 1
#  lsAlertColor = fAlertProcessor(liAlertRed, liAlertYellow)


  fhHtml.writelines("<html>")
  fhHtml.writelines("<body>")
  fhHtml.writelines("<center><h2>Environments</h2></center>")
  fhHtml.writelines(fSetUpdatedTime())
  fhHtml.writelines("<h3>Overall Health</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr>")
  fhHtml.writelines("<td bgcolor='#CCCCCC'><b>Care Environments</b></td>")
  fhHtml.writelines("<td bgcolor='#00FF00'><b>Healthy</b></td>")
  fhHtml.writelines("</tr>")
  fhHtml.writelines("<tr>")
  fhHtml.writelines("<td bgcolor='#CCCCCC'><b>HCC Environments</b></td>")
  fhHtml.writelines("<td bgcolor='#FFFF00'><b>UnHealthy</b></td>")
  fhHtml.writelines("</tr>")
  fhHtml.writelines("<tr>")
  fhHtml.writelines("<td bgcolor='#CCCCCC'><b>Pipeline Environments</b></td>")
  fhHtml.writelines("<td bgcolor='#FFFFFF'><b>Unknown</b></td>")
  fhHtml.writelines("</tr>")
  fhHtml.writelines("</table>")

  fhHtml.writelines("<h3>Care Production</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://care.apixio.com' target='_blank'><font color='#FFFFFF'><b>care.apixio.com</b></font></a></td></tr>")

  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.AWS.Server.Information.html                                        ", "AWS Server Information        ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.Apixio.Service.Information.html                                    ", "Apixio Service Information    ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.usr.share.apache-tomcat-7.0.47.logs.catalina.out.html              ", "Tomcat catalina.out           ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.boot.log.html                                                 ", "Linux boot.log                ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.yum.log.html                                                  ", "Linux yum.log                 ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.cron.html                                                     ", "Linux cron Logs               ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.secure.html                                                   ", "Linux secure Logs             ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.lastlog.html                                                       ", "Linux lastlog Command         ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.last.html                                                          ", "Linux last Command            ")
  fhHtml.writelines("</table>")

# *AB* *AB* *AB*

  fhHtml.writelines("<h3>HCC Advanced</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://hccadv.apixio.com' target='_blank'><font color='#FFFFFF'><b>hccadv.apixio.com</b></font></a></td></tr>")

  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.AWS.Server.Information.html                                        ", "AWS Server Information        ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.Apixio.Service.Information.html                                    ", "Apixio Service Information    ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.usr.share.apache-tomcat-7.0.47.logs.catalina.out.html              ", "Tomcat catalina.out           ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.boot.log.html                                                 ", "Linux boot.log                ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.yum.log.html                                                  ", "Linux yum.log                 ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.cron.html                                                     ", "Linux cron Logs               ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com..log.secure.html                                                   ", "Linux secure Logs             ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.lastlog.html                                                       ", "Linux lastlog Command         ")
  fCheckHealth(fhHtml, "html/qdagent.py.care.apixio.com.last.html                                                          ", "Linux last Command            ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com.AWS.Server.Information.html                                      ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com.Apixio.Service.Information.html                                  ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com.Apixio.Login.Information.html                                    ' target='frame3'><font color='#000000'>Apixio Login Information      </font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccadv.apixio.com:8443/ctrl/router/configuration                                           ' target='frame3'><font color='#000000'>Apixio Router Config / Version</font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccadv.apixio.com:8443/ctrl/data/routing_summary                                           ' target='frame3'><font color='#000000'>Apixio Routing Summary        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com.usr.lib.apx-hcc.hcc_project.hcc_project.settings.local.py.html   ' target='frame3'><font color='#000000'>Apixio local.py               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.apx-hcc.apx-hcc.log.html                                    ' target='frame3'><font color='#000000'>Apixio apx-hcc.log            </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.apx-hcc.apx-hcc-console.log.html                            ' target='frame3'><font color='#000000'>Apixio apx-hcc-console.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.apx-hcc.apx-hcc-error.log.html                              ' target='frame3'><font color='#000000'>Apixio apx-hcc-error.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.apx-hcc.apx-hcc-event.log.html                              ' target='frame3'><font color='#000000'>Apixio apx-hcc-event.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.apx-hcc.apx-hcc-warning.log.html                            ' target='frame3'><font color='#000000'>Apixio apx-hcc-warning.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.apx-opprouter.apx-opprouter.log.html                        ' target='frame3'><font color='#000000'>Apixio apx-opprouter.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.httpd.access_log.html                                       ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.httpd.error_log.html                                        ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.boot.log.html                                               ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.yum.log.html                                                ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.cron.html                                                   ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com..log.secure.html                                                 ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com.lastlog.html                                                     ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccadv.apixio.com.last.html                                                        ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<h3>HCC Demo</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://hccdemo.apixio.com' target='_blank'><font color='#FFFFFF'><b>hccdemo.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com.AWS.Server.Information.html                                     ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com.Apixio.Service.Information.html                                 ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com.Apixio.Login.Information.html                                   ' target='frame3'><font color='#000000'>Apixio Login Information      </font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccdemo.apixio.com:8443/ctrl/router/configuration                                          ' target='frame3'><font color='#000000'>Apixio Router Config / Version</font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccdemo.apixio.com:8443/ctrl/data/routing_summary                                          ' target='frame3'><font color='#000000'>Apixio Routing Summary        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com.usr.lib.apx-hcc.hcc_project.hcc_project.settings.local.py.html  ' target='frame3'><font color='#000000'>Apixio local.py               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.apx-hcc.apx-hcc.log.html                                   ' target='frame3'><font color='#000000'>Apixio apx-hcc.log            </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.apx-hcc.apx-hcc-console.log.html                           ' target='frame3'><font color='#000000'>Apixio apx-hcc-console.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.apx-hcc.apx-hcc-error.log.html                             ' target='frame3'><font color='#000000'>Apixio apx-hcc-error.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.apx-hcc.apx-hcc-event.log.html                             ' target='frame3'><font color='#000000'>Apixio apx-hcc-event.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.apx-hcc.apx-hcc-warning.log.html                           ' target='frame3'><font color='#000000'>Apixio apx-hcc-warning.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.apx-opprouter.apx-opprouter.log.html                       ' target='frame3'><font color='#000000'>Apixio apx-opprouter.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.httpd.access_log.html                                      ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.httpd.error_log.html                                       ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.boot.log.html                                              ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.yum.log.html                                               ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.cron.html                                                  ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com..log.secure.html                                                ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com.lastlog.html                                                    ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccdemo.apixio.com.last.html                                                       ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<h3>HCC Integration</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://hccint.apixio.com' target='_blank'><font color='#FFFFFF'><b>hccint.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com.AWS.Server.Information.html                                      ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com.Apixio.Service.Information.html                                  ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com.Apixio.Login.Information.html                                    ' target='frame3'><font color='#000000'>Apixio Login Information      </font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccint.apixio.com:8443/ctrl/router/configuration                                           ' target='frame3'><font color='#000000'>Apixio Router Config / Version</font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccint.apixio.com:8443/ctrl/data/routing_summary                                           ' target='frame3'><font color='#000000'>Apixio Routing Summary        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com.usr.lib.apx-hcc.hcc_project.hcc_project.settings.local.py.html   ' target='frame3'><font color='#000000'>Apixio local.py               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.apx-hcc.apx-hcc.log.html                                    ' target='frame3'><font color='#000000'>Apixio apx-hcc.log            </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.apx-hcc.apx-hcc-console.log.html                            ' target='frame3'><font color='#000000'>Apixio apx-hcc-console.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.apx-hcc.apx-hcc-error.log.html                              ' target='frame3'><font color='#000000'>Apixio apx-hcc-error.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.apx-hcc.apx-hcc-event.log.html                              ' target='frame3'><font color='#000000'>Apixio apx-hcc-event.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.apx-hcc.apx-hcc-warning.log.html                            ' target='frame3'><font color='#000000'>Apixio apx-hcc-warning.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.apx-opprouter.apx-opprouter.log.html                        ' target='frame3'><font color='#000000'>Apixio apx-opprouter.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.httpd.access_log.html                                       ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.httpd.error_log.html                                        ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.boot.log.html                                               ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.yum.log.html                                                ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.cron.html                                                   ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com..log.secure.html                                                 ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com.lastlog.html                                                     ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccint.apixio.com.last.html                                                        ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<h3>HCC Production</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://hcc.apixio.com' target='_blank'><font color='#FFFFFF'><b>hcc.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com.AWS.Server.Information.html                                         ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com.Apixio.Service.Information.html                                     ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com.Apixio.Login.Information.html                                       ' target='frame3'><font color='#000000'>Apixio Login Information      </font></a><br>  ")
  fhHtml.writelines("          <a href='https://hcc.apixio.com:8443/ctrl/router/configuration                                              ' target='frame3'><font color='#000000'>Apixio Router Config / Version</font></a><br>  ")
  fhHtml.writelines("          <a href='https://hcc.apixio.com:8443/ctrl/data/routing_summary                                              ' target='frame3'><font color='#000000'>Apixio Routing Summary        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com.usr.lib.apx-hcc.hcc_project.hcc_project.settings.local.py.html      ' target='frame3'><font color='#000000'>Apixio local.py               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.apx-hcc.apx-hcc.log.html                                       ' target='frame3'><font color='#000000'>Apixio apx-hcc.log            </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.apx-hcc.apx-hcc-console.log.html                               ' target='frame3'><font color='#000000'>Apixio apx-hcc-console.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.apx-hcc.apx-hcc-error.log.html                                 ' target='frame3'><font color='#000000'>Apixio apx-hcc-error.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.apx-hcc.apx-hcc-event.log.html                                 ' target='frame3'><font color='#000000'>Apixio apx-hcc-event.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.apx-hcc.apx-hcc-warning.log.html                               ' target='frame3'><font color='#000000'>Apixio apx-hcc-warning.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.apx-opprouter.apx-opprouter.log.html                           ' target='frame3'><font color='#000000'>Apixio apx-opprouter.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.httpd.access_log.html                                          ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.httpd.error_log.html                                           ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.boot.log.html                                                  ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.yum.log.html                                                   ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.cron.html                                                      ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com..log.secure.html                                                    ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com.lastlog.html                                                        ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hcc.apixio.com.last.html                                                           ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://acladmin-stg1-node1.apixio.net' target='_blank'><font color='#FFFFFF'><b>acladmin-stg1-node1.apixio.net</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.net.AWS.Server.Information.html                         ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.net.Apixio.Service.Information.html                     ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.net..log.apx-accounts.apx-accounts.log.html             ' target='frame3'><font color='#000000'>Apixio apx-accounts.log       </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.net..log.httpd.access_log.html                          ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.net..log.httpd.error_log.html                           ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.com..log.boot.log.html                                  ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.com..log.yum.log.html                                   ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.com..log.cron.html                                      ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.com..log.secure.html                                    ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.com.lastlog.html                                        ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.acladmin-stg1-node1.apixio.com.last.html                                           ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://bundler-prd.apixio.com' target='_blank'><font color='#FFFFFF'><b>bundler-prd.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com.AWS.Server.Information.html                                 ' target='frame3'><font color='#000000'>AWS Server Information         </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com.Apixio.Service.Information.html                             ' target='frame3'><font color='#000000'>Apixio Service Information     </font></a><br> ")
  fhHtml.writelines("          <a href='https://bundler-prd.apixio.com:8444/hcc/bundler/configuration                                      ' target='frame3'><font color='#000000'>Apixio Bundler Config / Version</font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com..log.apx-bundler.apx-bundler.log.html                       ' target='frame3'><font color='#000000'>Apixio apx-bundler.log         </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com..log.boot.log.html                                          ' target='frame3'><font color='#000000'>Linux boot.log                 </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com..log.yum.log.html                                           ' target='frame3'><font color='#000000'>Linux yum.log                  </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com..log.cron.html                                              ' target='frame3'><font color='#000000'>Linux cron Logs                </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com..log.secure.html                                            ' target='frame3'><font color='#000000'>Linux secure Logs              </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com.lastlog.html                                                ' target='frame3'><font color='#000000'>Linux lastlog Command          </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-prd.apixio.com.last.html                                                   ' target='frame3'><font color='#000000'>Linux last Command             </font></a><br> ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://microservices-prd.apixio.com' target='_blank'><font color='#FFFFFF'><b>microservices-prd.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com.AWS.Server.Information.html                           ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com.Apixio.Service.Information.html                       ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          apixio-rest-acl Logs: <a href='https://apixio.atlassian.net/browse/HCC-160                                  ' target='_blank'><font color='#000000'>HCC-160                       </font></a><br>  ")
  fhHtml.writelines("          rest-tokenizer Logs:  <a href='https://apixio.atlassian.net/browse/HCC-161                                  ' target='_blank'><font color='#000000'>HCC-161                       </font></a><br>  ")
  fhHtml.writelines("          rest-useracct Logs:   <a href='https://apixio.atlassian.net/browse/HCC-162                                  ' target='_blank'><font color='#000000'>HCC-162                       </font></a><br>  ")
  fhHtml.writelines("          apx-accounts Logs:    <a href='https://apixio.atlassian.net/browse/HCC-163                                  ' target='_blank'><font color='#000000'>HHC-163                       </font></a><br>  ")
  fhHtml.writelines("          apx-dataorchestrator Log: <a href='https://apixio.atlassian.net/browse/HCC-164                              ' target='_blank'><font color='#000000'>HCC-164                       </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com..log.boot.log.html                                    ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com..log.yum.log.html                                     ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com..log.cron.html                                        ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com..log.secure.html                                      ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com.lastlog.html                                          ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-prd.apixio.com.last.html                                             ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<h3>HCC Staging</h3>")
  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://hccstage.apixio.com' target='_blank'><font color='#FFFFFF'><b>hccstage.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com.AWS.Server.Information.html                                    ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com.Apixio.Service.Information.html                                ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com.Apixio.Login.Information.html                                  ' target='frame3'><font color='#000000'>Apixio Login Information      </font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccstage.apixio.com:8443/ctrl/router/configuration                                         ' target='frame3'><font color='#000000'>Apixio Router Config / Version</font></a><br>  ")
  fhHtml.writelines("          <a href='https://hccstage.apixio.com:8443/ctrl/data/routing_summary                                         ' target='frame3'><font color='#000000'>Apixio Routing Summary        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com.usr.lib.apx-hcc.hcc_project.hcc_project.settings.local.py.html ' target='frame3'><font color='#000000'>Apixio local.py               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.apx-hcc.apx-hcc.log.html                                  ' target='frame3'><font color='#000000'>Apixio apx-hcc.log            </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.apx-hcc.apx-hcc-console.log.html                          ' target='frame3'><font color='#000000'>Apixio apx-hcc-console.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.apx-hcc.apx-hcc-error.log.html                            ' target='frame3'><font color='#000000'>Apixio apx-hcc-error.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.apx-hcc.apx-hcc-event.log.html                            ' target='frame3'><font color='#000000'>Apixio apx-hcc-event.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.apx-hcc.apx-hcc-warning.log.html                          ' target='frame3'><font color='#000000'>Apixio apx-hcc-warning.log    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.apx-opprouter.apx-opprouter.log.html                      ' target='frame3'><font color='#000000'>Apixio apx-opprouter.log      </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.httpd.access_log.html                                     ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.httpd.error_log.html                                      ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.boot.log.html                                             ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.yum.log.html                                              ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.cron.html                                                 ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com..log.secure.html                                               ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com.lastlog.html                                                   ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.hccstage.apixio.com.last.html                                                      ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://accounts-stg1-node1.apixio.net' target='_blank'><font color='#FFFFFF'><b>accounts-stg1-node1.apixio.net</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.net.AWS.Server.Information.html                         ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.net.Apixio.Service.Information.html                     ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.net..log.apx-accounts.apx-accounts.log.html             ' target='frame3'><font color='#000000'>Apixio apx-accounts.log       </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.net..log.httpd.access_log.html                          ' target='frame3'><font color='#000000'>HTTP access_log               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.net..log.httpd.error_log.html                           ' target='frame3'><font color='#000000'>HTTP error_log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.com..log.boot.log.html                                  ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.com..log.yum.log.html                                   ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.com..log.cron.html                                      ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.com..log.secure.html                                    ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.com.lastlog.html                                        ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.accounts-stg1-node1.apixio.com.last.html                                           ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://bundler-stg.apixio.com' target='_blank'><font color='#FFFFFF'><b>bundler-stg.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com.AWS.Server.Information.html                                 ' target='frame3'><font color='#000000'>AWS Server Information         </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com.Apixio.Service.Information.html                             ' target='frame3'><font color='#000000'>Apixio Service Information     </font></a><br> ")
  fhHtml.writelines("          <a href='https://bundler-stg.apixio.com:8444/hcc/bundler/configuration                                      ' target='frame3'><font color='#000000'>Apixio Bundler Config / Version</font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com..log.apx-bundler.apx-bundler.log.html                       ' target='frame3'><font color='#000000'>Apixio apx-bundler.log         </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com..log.boot.log.html                                          ' target='frame3'><font color='#000000'>Linux boot.log                 </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com..log.yum.log.html                                           ' target='frame3'><font color='#000000'>Linux yum.log                  </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com..log.cron.html                                              ' target='frame3'><font color='#000000'>Linux cron Logs                </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com..log.secure.html                                            ' target='frame3'><font color='#000000'>Linux secure Logs              </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com.lastlog.html                                                ' target='frame3'><font color='#000000'>Linux lastlog Command          </font></a><br> ")
  fhHtml.writelines("          <a href='html/qdagent.py.bundler-stg.apixio.com.last.html                                                   ' target='frame3'><font color='#000000'>Linux last Command             </font></a><br> ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<table>")
  fhHtml.writelines("<tr><td bgcolor='#000000'><a href='https://microservices-stg.apixio.com' target='_blank'><font color='#FFFFFF'><b>microservices-stg.apixio.com</b></font></a></td></tr>")

  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com.AWS.Server.Information.html                           ' target='frame3'><font color='#000000'>AWS Server Information        </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com.Apixio.Service.Information.html                       ' target='frame3'><font color='#000000'>Apixio Service Information    </font></a><br>  ")
  fhHtml.writelines("          apixio-rest-acl Logs: <a href='https://apixio.atlassian.net/browse/HCC-160                                  ' target='_blank'><font color='#000000'>HCC-160                       </font></a><br>  ")
  fhHtml.writelines("          rest-tokenizer Logs:  <a href='https://apixio.atlassian.net/browse/HCC-161                                  ' target='_blank'><font color='#000000'>HCC-161                       </font></a><br>  ")
  fhHtml.writelines("          rest-useracct Logs:   <a href='https://apixio.atlassian.net/browse/HCC-162                                  ' target='_blank'><font color='#000000'>HCC-162                       </font></a><br>  ")
  fhHtml.writelines("          apx-accounts Logs:    <a href='https://apixio.atlassian.net/browse/HCC-163                                  ' target='_blank'><font color='#000000'>HHC-163                       </font></a><br>  ")
  fhHtml.writelines("          apx-dataorchestrator Log: <a href='https://apixio.atlassian.net/browse/HCC-164                              ' target='_blank'><font color='#000000'>HCC-164                       </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com..log.boot.log.html                                    ' target='frame3'><font color='#000000'>Linux boot.log                </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com..log.yum.log.html                                     ' target='frame3'><font color='#000000'>Linux yum.log                 </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com..log.cron.html                                        ' target='frame3'><font color='#000000'>Linux cron Logs               </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com..log.secure.html                                      ' target='frame3'><font color='#000000'>Linux secure Logs             </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com.lastlog.html                                          ' target='frame3'><font color='#000000'>Linux lastlog Command         </font></a><br>  ")
  fhHtml.writelines("          <a href='html/qdagent.py.microservices-stg.apixio.com.last.html                                             ' target='frame3'><font color='#000000'>Linux last Command            </font></a><br>  ")

  fhHtml.writelines("</table>")

  fhHtml.writelines("<h3>Pipeline Production</h3>")
  fhHtml.writelines("... Need More Information ...")
  fhHtml.writelines("<h3>Pipeline Staging</h3>")
  fhHtml.writelines("... Need More Information ...")
  fhHtml.writelines("<br><br>")
  fhHtml.writelines("<h3>Legend</h3>")
  fhHtml.writelines("<table border=1>")
  fhHtml.writelines("<tr><td bgcolor='#00FF00'><font color='#000000'>App/Service/System is Healthy</font></td></tr>")
  fhHtml.writelines("<tr><td bgcolor='#FFFF00'><font color='#000000'>App/Service/System is Unhealthy</font></td></tr>")
  fhHtml.writelines("<tr><td bgcolor='#FF0000'><font color='#000000'>App/Service/System is Critical</font></td></tr>")
  fhHtml.writelines("<tr><td bgcolor='#FFFFFF'><font color='#000000'>App/Service/System is Unknown</font></td></tr>")
  fhHtml.writelines("</table>")
  fhHtml.writelines("<h3>Notes</h3>")
  fhHtml.writelines("<li>Monitoring runs every 2 minutes</li>")
  fhHtml.writelines("<li>Red alerts go to qa@apixio.com</li>")
  fhHtml.writelines("<li>Send feedback to <a href='mailto:abeyk@apixio.com' target='_blank'>abeyk@apixio.com</a></li>")
  fhHtml.writelines("</body>")
  fhHtml.writelines("</html>")
  fhHtml.close()
  print strftime("%Y-%m-%d %H:%M:%S ") + "Completed Creating " + gsFrameFile
  fLog.info("Completed Creating " + gsFrameFile)
  return 0

def fSetUpdatedTime(): ####################################################################################################
  fLog.info("fSetUpdatedTime")
  UTC = Zone(0,False,"UTC")
  PST = Zone(-8,True,"PST") # *AB* Daylight Savings Time or DST set to True
  liCurrentUTCDateTime = datetime.strptime(strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
  liCurrentUTCDateTime = liCurrentUTCDateTime.replace(tzinfo=UTC)
  liCurrentPSTDateTime = liCurrentUTCDateTime.astimezone(PST)
  lsCurrentUTCDateTime = str(liCurrentUTCDateTime)[:-6]
  lsCurrentPSTDateTime = str(liCurrentPSTDateTime)[:-6]
  gsLastUpdatedTime = "<h5>Page last updated on: " + lsCurrentUTCDateTime + " UTC<br>Page last updated on: " + lsCurrentPSTDateTime + " PST</h5>"
  return gsLastUpdatedTime

def fAlertProcessor(liAlertRed, liAlertYellow): ####################################################################################################
  fLog.info("fAlertProcessor")
  if liAlertRed > 0:
    lsAlertColor = "red"
  elif liAlertYellow > 0:
    lsAlertColor = "yellow"
  else:
    lsAlertColor = "green"
  return lsAlertColor

def fCheckHealth(fhHtml, lsFile, lsTitle): ####################################################################################################
  fLog.info("fCheckHealth")
  if os.path.isfile(lsFile + ".green"):
    lsHtml = "<tr><td bgcolor='" + gsGreen  + "'><a href='" + lsFile + "' target='frame3'><font color='#000000'>" + lsTitle + "</font></a></td></tr>"
  elif os.path.isfile(lsFile + ".yellow"):
    lsHtml = "<tr><td bgcolor='" + gsYellow + "'><a href='" + lsFile + "' target='frame3'><font color='#000000'>" + lsTitle + "</font></a></td></tr>"
  elif os.path.isfile(lsFile + ".red"):
    lsHtml = "<tr><td bgcolor='" + gsRed    + "'><a href='" + lsFile + "' target='frame3'><font color='#000000'>" + lsTitle + "</font></a></td></tr>"
  else:
    lsHtml = "<tr><td bgcolor='" + gsWhite  + "'><a href='" + lsFile + "' target='frame3'><font color='#000000'>" + lsTitle + "</font></a></td></tr>"
  fhHtml.writelines(lsHtml)
  return 0

# BEGIN MAIN PROGRAM ####################################################################################################

fRunMainProgram()

# END MAIN PROGRAM ####################################################################################################

