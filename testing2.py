import smtplib
"""this is some test documentation in the function"""

# Send the mail
server = smtplib.SMTP('vsrv-mail-01.clsi.ca')
server.starttls()
server.login('lus', '1q2aw3zse4')
server.sendmail('sunny.lu@lightsource.ca', 'sunny.lu.sl@gmail.com', '')
server.quit()