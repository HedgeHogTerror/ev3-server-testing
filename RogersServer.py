#!/usr/bin/python
import BotSpeakPaths
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import thread
import threading
import time

info = True
BotSpeak = []
VAR = {'VER':0.1, 'HI':1, 'LO':0}

PORT_NUMBER = 8000

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/index.html"

		try:
			#Check the file extension required and
			#set the right mime type

			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".gif"):
				mimetype='image/gif'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
#		print self.path
		
		if self.path=="/motor":
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],}
			)
			
			print form
			
			if form['cmd'].value == 'run':
				for i in range(0,3):
					speed = 'Speed{}'.format(i)
					motor = open(BotSpeakPaths.mspeed.format(i),'r+')
					motor.write(form[speed].value + '\n')
					motor.close
					motor = open(BotSpeakPaths.mrun.format(i),'r+')
					motor.write('1\n')
					motor.close
			else:
				for i in range(0,3):
					speed = 'Speed{}'.format(i)
					motor = open(BotSpeakPaths.mrun.format(i),'r+')
					motor.write('0\n')
					motor.close
			self.send_response(200)
			self.end_headers()
			self.wfile.write("success")
			return			

		if self.path=="/led":
			form2 = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			
			print form2
			
			if form2['cmd'].value == 'update':
				LED = open(BotSpeakPaths.ledbright.format('red','right'),'r+')
				LED.write(form2['LEDRR'].value + '\n')
				LED.close
				LED = open(BotSpeakPaths.ledbright.format('red','left'),'r+')
				LED.write(form2['LEDLR'].value + '\n')
				LED.close
				LED = open(BotSpeakPaths.ledbright.format('green','right'),'r+')
				LED.write(form2['LEDRG'].value + '\n')
				LED.close
				LED = open(BotSpeakPaths.ledbright.format('green','left'),'r+')
				LED.write(form2['LEDLG'].value + '\n')
				LED.close

			self.send_response(200)
			self.end_headers()
			self.wfile.write("success")
			return			

		if self.path=="/BotSpeak":
			form3 = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],}
			)
			
			print form3
			
			global BotSpeak 
			BotSpeak = form3['BotSpeak'].value.split('\r\n')
			self.send_response(200)
			self.end_headers()
			self.wfile.write(BotSpeak)
			return			


			
#This is a thread that runs the web server 
def WebServerThread():			
	try:
		#Create a web server and define the handler to manage the
		#incoming request
		server = HTTPServer(('', PORT_NUMBER), myHandler)
		print 'Started httpserver on port ' , PORT_NUMBER
		
		#Wait forever for incoming htto requests
		server.serve_forever()

	except KeyboardInterrupt:
		print '^C received, shutting down the web server'
		server.socket.close()


# Runs the web server thread
thread.start_new_thread(WebServerThread,())		


def PWM(channel,value):
	port=int(channel)
	if value.isdigit():
		speed = float(value)
	else: speed = float(VAR[value])
	print ('Setting PWM {} to {}').format(port,speed)
	return speed

def AI(value):
	return 1024
	
OPS = {'PWM':PWM, 'AI':AI}

#Execute BotSpeak Command
def ExecuteCommand(command):
	if command == '':
		return command
	cmd,space,value = command.partition(' ')
	channel = '0'
	source = ''
	if ',' in value:
		source,space,value = value.partition(',')
	if '[' in source:
		source,space,channel = source.partition('[')
		print channel
		channel = channel.split(']')[0]
	if (source == 'AO'): source = 'PWM'
	if cmd == 'SET':
		print 'Setting '+source+' [' + channel + '] to ' + value
		
		OPS[source] (channel,value)
#		if (source == 'PWM'):  PWM(source, value)
#		elif (source == '
#		exec('%s = %f' % (source,float(value)))
		return value
	elif cmd == 'GET':
		return value
	elif cmd == 'WAIT':
		waitTime = float(value) / 1000
		time.sleep(waitTime)
		return value
		
#Forever loop
PWM=[0,0,0,0,0,0,0,0]  #... A,B,C,D,LeftLED Red, LeftLED Green, RightLED R, RL G
AI=[0,0,0,0]   #... ports 1,2,3,4


while True:
	if len(BotSpeak) > 0:	
		for command in BotSpeak:
			print PWM
			print 'Running ' + command + ' returned ' + ExecuteCommand(command)
		BotSpeak = []
	else: 
		time.sleep(0.5)

