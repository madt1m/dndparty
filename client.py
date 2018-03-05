import socket
import sys
import select
from termcolor import colored
import re

def clearPreviousLine():
	"""\033[F = go back to previuos line, 
   	   \033[K = clear line"""
	sys.stdout.write("\033[F")
	sys.stdout.write("\033[K")
	sys.stdout.flush()

if(len(sys.argv) < 3):
	print("Usage: DnD_chatroom.py server_address server_port")
	sys.exit()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP = sys.argv[1]
PORT = int(sys.argv[2])
server.connect((IP, PORT))

print("Connected to server: %s on port %d"% (IP,PORT)) 

inputStreamList = [sys.stdin, server]
"""
Registration Phase:
	The first messages from the server are blocking until registration is
	done.
	Next is character creation, both server and client must have same character 
	stat and inventory file.
	The GameMaster must be both Server and Client and to this purpose server and 	    client scripts must be included into some other one, being able to switch
	from one to the other as needed.
	
"""
"""
Chat Phase:
	todo: Need to define special commands.
"""
commands = ["\do", "www"]
# mapping commands to numbers which will be used as indexes for choosing the color
#dictionary = dict([(y,x+1) for x,y in enumerate(sorted(set(commands)))])
colorsMap = {"\do":"yellow", "www":"white"}
first = True
while True:
	inputStreamList = [sys.stdin, server]
	read_socket, write_socket, error_socket = select.select(inputStreamList,[],[])
	if first == True: 
		first = False
		msg = server.recv(2048) # welcome Message expected
		if msg:	
			print(msg.decode()+"<You> ", end ="")
			
	else:
		for sock in read_socket: #inputStreamList:
			if sock == server:
				# write to stout from server
				msg = sock.recv(2048)
				if msg:
					msg = msg.decode()
					sender = re.findall("<.*>|$", msg)[0]
					msg = msg[(len(sender)+1):]
					if msg[0] == "\\":
						for command in commands:
							msgBegin = msg[:len(command)]
							if msgBegin == command:
								msg = colored(msg[len(command):], colorsMap[command])
					msg = sender + " " + msg
					sys.stdout.write('\r'+msg)
					sys.stdout.write("<You> ")
					sys.stdout.flush()
				else:
					clearPreviousLine()
					sys.stdout.write("\r<System> Connection broken, exiting chatroom\n")
					sys.stdout.flush()			
					sys.exit()
			else:	# case = stdin
				# send to server + write to stout
				msg = sock.readline()
				server.send(msg.encode())
				if msg[0] == "\\":
				
					# case special command
					for command in commands:
						msgBegin = msg[:len(command)]
						if msgBegin == command:
							msg = colored(msg[len(command):], colorsMap[command])	
					clearPreviousLine()
					sys.stdout.write('\r<You> '+msg)
					sys.stdout.flush()
				sys.stdout.write("<You> ")
				sys.stdout.flush() # Force write buffer to terminal
			

server.close()

