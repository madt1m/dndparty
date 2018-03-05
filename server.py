import socket
import sys
import fcntl
import struct
import threading
import re
import os

lock = threading.RLock()
sDirectory = "dndServer"
if not os.path.exists(sDirectory):
	os.makedirs(sDirectory)
def clientThread(conn, addr):
	print("New client connected: " + addr[0])
	welcome = "Welcome to the chatroom, mate!\n"
	conn.send(welcome.encode())
	while True:
		try:
			#print("Waiting for messages...")
			msg = conn.recv(4096)
			#print("Received from "+ addr[0])
			#print("\n"+msg.decode())
			#mex = "You sent me this: " + msg.decode()
			#conn.send(mex.encode())
			if msg is not None:
				msg_to_send = "<"+ addr[0] + "> " + msg.decode()
				print(msg_to_send, end="")
				"""print("To:")
				for client in clients:
					print(client.getpeername())"""
				with lock:
					try:
						f = open(sDirectory+"/chatlog.txt", "a+")
						try:
							f.write(msg_to_send)
						finally:
							f.close()
					except:
						pass        
				broadcast(conn, msg_to_send)

			else:
				remove(conn)
				break
		except:
			continue
	

def broadcast(connection, message):
	for client in clients:
		if client != connection:
			try:
				client.send(message.encode())
			except:
				client.close()
				remove(client)

def remove(connection):
	if connection in clients:
		clients.remove(connection)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])


if(len(sys.argv) is not 3):
	print("Usage: python dndparty_server.py <IP address> <port>")
	exit()

# Extract interface and port from the command line args
ip = sys.argv[1]
PORT = sys.argv[2]

# A list to keep track of all the clients
clients = []

# Create server sockets, bind it to the right iface and port and limit conns to 5
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, int(PORT)))
print("[+] Server running on address "+ip+" and port "+PORT)
server.listen(100)
while True:
	# Register a new client
	conn, addr = server.accept()
	print("Got a connection...")
	clients.append(conn)
	t = threading.Thread(target=clientThread, args=(conn, addr))
	t.start()
sys.exit()	
