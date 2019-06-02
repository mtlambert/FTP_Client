import socket
from os import listdir

# enter host IP address
HOST = ""
PORT = 65535
commands = ('view', 'send', 'store', 'end')
s = socket.socket()

# creates connection to host machine
def connect():
    try:
        s.connect((HOST, PORT))
    except socket.error as msg:
        print("Error connecting to server: " + str(msg))

# takes file name or file path and returns the size of the file, returns false if a directory is entered
def get_file_size(file_path):
	try:
		f = open(file_path, 'rb')
		size = len(f.read())
		f.close()
		return size
	except IsADirectoryError:
		return False

# takes a file path, default is local directory, and returns a list of files in that directory
def get_dir_list(PATH=''):
    if PATH:
        full_dir_list = listdir(PATH)
        dir_list = []
        for i in full_dir_list:
            if get_file_size(i):
                dir_list.append(i)
        return dir_list
    else:
        full_dir_list = listdir()
        dir_list = []
        for i in full_dir_list:
            if get_file_size(i):
                dir_list.append(i)
        return dir_list

# formats get_dir_list() output and converts to string before sending
def format_dir_list(PATH=''):
    dir_list = get_dir_list(PATH)
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
            s.send(str(size).encode('utf-8'))
            s.sendall(message)
        else:
            s.send(str(size).encode('utf-8'))
            s.sendall(message.encode('utf-8'))
    except socket.error as msg:
        print("Sending error: " + str(msg))

# recieves an encoded string from host.
#   if first message specifies data package is being sent it calls store_file()
def recieve(file_name=''):
    size = s.recv(1024).decode('utf-8').split()
    if size[0] == 'd':
        size_recieved = 0
        data = b''
        while size_recieved < int(size[1]):
            chunk = s.recv(int(size[1]) - size_recieved)
            size_recieved += len(chunk)
            data += chunk
            # uncomment below to add download percent printing to host
            # print download percent
            print(str(round(size_recieved/int(size[1]) * 100)) +"%")
        store_file(data, file_name)
        return "File recieved"
    else:
        data = s.recv(int(size[0])).decode('utf-8')
        return data

# takes byte-like data and a file name or file path to store data
def store_file(data, file_path):
    f = open(file_path, 'wb')
    f.write(data)
    f.close()

# takes a local directory file name or file path as a parameter and returns that file as
#   byte-like data to be sent
def prep_data_to_store(file_path):
    f = open(file_path, 'rb')
    data = f.read()
    f.close()
    return data

# if a file to be stored or sent already exists, adds "_1" to file name to prevent overwriting
def rename_file(file_name):
    file_name = file_name.split('.')
    file_name[0] += "_1"
    file_name = ".".join(file_name)
    return file_name



print("FTP Client Started")

try:
    connect()
except socket.error as msg:
    print("Sorry, we were unable to connect to your local server: " + str(msg))

# recieve initial connection message from host
print(recieve())
while True:
    try:
        response_to_server = str(input(">> "))
        send(response_to_server)
        client_response = response_to_server.split()
        if client_response[0] in commands:
            # process for calling 'view' functionality
            if client_response[0] == 'view' and len(client_response) == 1:
                print(recieve())
            # process for calling 'send' functionality
            elif client_response[0] == 'send' and len(client_response) == 2:
                if client_response[1] in get_dir_list():
                    recieve(rename_file(client_response[1]))
                    print(rename_file(client_response[1]) + " recieved")
                else:
                    recieve(client_response[1])
                    print(client_response[1] + " recieved")
            # process for calling 'store' functionality
            elif client_response[0] == 'store' and len(client_response) == 2:
                if client_response[1] in get_dir_list():
                    print(recieve())
                    send(prep_data_to_store(client_response[1]), get_file_size(client_response[1]), True)
                    print(client_response[1] + " stored on server")
                else:
                    print(recieve())
                    send("Client attempted to send file, but was unable to find source")
                    print(" Could not find " + client_response[1])
            # process for calling 'end' connection functionality
            elif client_response[0] == 'end' and len(client_response) == 1:
                print(recieve())
                s.close()
                break
            else:
                print(recieve())
        # if invalid or incorrectly formated requests are sent to host,
        #   host returns error message which is recieved below
        else:
            print(recieve())
    except socket.error as msg:
        print("Communication error: " + str(msg))
        continue
