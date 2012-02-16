"""
Simple Mail Reporter, Just in case you can't live with your server.
created by : Chen Wei @ 2011.12.12
"""
import smtplib

class MailReporter:
    def __init__(self):
        self.fromaddr = "38@keg.org" 
        self.toaddrs  = ["cleverdie@gmail.com"]
        self.subject  = "Google Scholar Report"

    def report(self, txt):
        """
        report crawler status
        """
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n%s\r\n"
           % (self.fromaddr, ", ".join(self.toaddrs), self.subject, txt))
        success = False
        trys	= 0

        while not success and trys < 3:
                try:
                        server = smtplib.SMTP("localhost")
                        server.sendmail(self.fromaddr, self.toaddrs, msg)
                        server.quit()
                        success = True
                        break
                except Exception:
                        trys+=1
