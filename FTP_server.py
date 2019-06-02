import socket
import datetime
from os import listdir

# insert host IP address below
HOST = ""
PORT = 65535
commands = ('view', 'send', 'store', 'end')
s = socket.socket()

# binds socket
def bind_socket():
    try:
        s.bind((HOST, PORT))
        print("FTP Server Started")
        print("Socket bound to " + HOST + " at port " + str(PORT))
    except socket.error as msg:
        print("Socket binding error: " + str(msg))

# begins socket listening and waits for connection from client
def establish_connection():
    s.listen()
    print("Listening...")
    global conn, addr;
    try:
        conn, addr = s.accept()
        print("Connected to client " + str(addr))
        log("Client connected to server.")
    except socket.error as msg:
        print("Error establishing connection to client: " + str(msg))

# takes file name from working directory and returns the size of the file, returns false if
#   a directory is entered
def get_file_size(file_name):
	try:
        # specify a file path to desired working directory
		f = open('file path goes here' + file_name, 'rb')
		size = len(f.read())
		f.close()
		return size
	except IsADirectoryError:
		return False

# returns a list of files in the specified working directory
def get_dir_list():
    # specify a file path to desired working directory
	full_dir_list = listdir('file path goes here')
	dir_list = []
	for i in full_dir_list:
		if get_file_size(i):
			dir_list.append(i)
	return dir_list

# formats get_dir_list() output and converts to string before sending
def format_dir_list():
    dir_list = get_dir_list()
    formated_list = ""
    for i in dir_list:
        formated_list += i + "  "
    return formated_list[:-2]

# takes a string as parameter to send to host or if data is set to True and a size is given
#   will transfer data package to host
def send(message, size=1024, data=False):
    try:
        if data:
            size = "d " + str(size)
            conn.send(str(size).encode('utf-8'))
            conn.sendall(message)
        else:
            conn.send(str(size).encode('utf-8'))
            conn.send(message.encode('utf-8'))
    except socket.error as msg:
        print("Sending error: " + str(msg))

# recieves an encoded string from host.
#   if first message specifies data package is being sent it calls store_file()
def recieve(file_name=''):
    size = conn.recv(1024).decode('utf-8').split()
    if size[0] == 'd':
        size_recieved = 0
        data = b''
        print(int(size[1]))
        while size_recieved < int(size[1]):
            chunk = conn.recv(int(size[1]) - size_recieved)
            size_recieved += len(chunk)
            data += chunk
        store_file(data, file_name)
        return "File recieved"
    else:
        data = conn.recv(int(size[0])).decode('utf-8')
        return data

# takes byte-like data and a file name or file path to store data
def store_file(data, file_name):
    # specify a file path to desired working directory
    f = open('file path goes here' + file_name, 'wb')
    f.write(data)
    f.close()
    log(file_name + " saved to server by client.")
    print(file_name + " saved to server by " + str(addr))

# takes a local directory file name or file path as a parameter and returns that file as
#   byte-like data to be sent
def prep_data_to_send(file_name):
    # specify a file path to desired working directory
    f = open('file path goes here' + file_name, 'rb')
    data = f.read()
    f.close()
    log("Sending " + file_name + " to client.")
    print("Sending " + file_name + " to " + str(addr))
    return data

# used to log client requests to specified log file
def log(message):
    # specify a file path below for log file
    f = open('file path for log goes here followed by /FTP_server_log', 'a')
    f.write(str(datetime.datetime.now()) + "/ Client " + str(addr) + "/ " + message + "\n")
    f.close()

# if a file to be stored or sent already exists, adds "_1" to file name to prevent overwriting
def rename_file(file_name):
    file_name = file_name.split('.')
    file_name[0] += "_1"
    file_name = ".".join(file_name)
    return file_name



bind_socket()

# outer while loop keeps server in a listening state even after client has ended
#   connection, incase further devices need to connect
while True:
    establish_connection()
    send("File transfer system connected:\nHello client. How may I be of service?")
    # inner while loop runs while connected to client, ends if client terminates connection.
    #   falls back to outer loop to wait for further connections
    while conn:
        try:
            client_response = recieve().split()
            print(client_response)
            if client_response[0] in commands:
                # process for calling 'view' functionality
                if client_response[0] == 'view' and len(client_response)==1:
                    send(format_dir_list())
                    log("Client requested dir_list.")
                # process for calling 'send' functionality
                elif client_response[0] == 'send' and len(client_response)==2:
                    if client_response[1] in get_dir_list():
                        send(prep_data_to_send(client_response[1]), get_file_size(client_response[1]), True)
                        log(" Client requested " + client_response[1])
                    else:
                        send("File not found")
                        log(" Client requested " + client_response[1] + " but file was not found")
                # process for calling 'store' functionality
                elif client_response[0] == 'store' and len(client_response)==2:
                    if client_response[1] in listdir():
                        send("Server ready to recieve file")
                        recieve(rename_file(client_response[1]))
                        log("Client stored " + rename_file(client_response[1]))
                    else:
                        send("Server ready to recieve file")
                        recieve(client_response[1])
                        log("Client stored " + client_response[1])
                # process for calling 'end' functionality
                elif client_response[0] == 'end' and len(client_response)==1:
                    send("Terminate command recieved.\nGoodbye")
                    conn.close()
                    print("Client terminated connection")
                    log("Client terminated connection.\n\n\n")
                    break
                # sends "Invalid command revieved" to client if invalid input is recieved
                else:
                    send("Invalid command recieved")
            # sends "Invalid command revieved" to client if invalid input is recieved
            else:
                print("sending invalid response")
                send("Invalid command recieved")
        except socket.error as msg:
            print("Communication error, connection lost: " + str(msg))
            log("Connection to client lost.")
            break
