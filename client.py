import socket
import sys
import select
from termcolor import colored

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
commands = ["\a", "www"]
# mapping commands to numbers which will be used as indexes for choosing the color
#dictionary = dict([(y,x+1) for x,y in enumerate(sorted(set(commands)))])
colorsMap = {"\a":"yellow", "www":"white"}
sys.stdout.write("<You> ")
sys.stdout.flush()

while True:
	inputStreamList = [sys.stdin, server]
	read_socket, write_socket, error_socket = select.select(inputStreamList,[],[])
	for sock in inputStreamList:
		if sock == server:
			# write to stout from server
			msg = sock.recv(2048)
			if msg:
				sys.stdout.write('\r'+msg.decode())
				sys.stdout.write("<You> ")
				sys.stdout.flush()
			else:
				sys.stdout.write("\r<System> Connection broken, exiting chatroom")
				#print("Connection broken, exiting chatroom")
				sys.exit()
		else:	# case = stdin
			# send to server + write to stout
			msg = sock.readline()
			if msg[0] == "\\":
				
				# case special command
				for command in commands:
					msgBegin = msg[:len(command)]
					if msgBegin == command:
						msg = colored(msg, colorsMap[command])	
				sys.stdout.write('\r'+msg)
				sys.stdout.flush()
			sys.stdout.write("<You> ")
			sys.stdout.flush() # Force write buffer to terminal
			server.send(msg.encode())

server.close()
