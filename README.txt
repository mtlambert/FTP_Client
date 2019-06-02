Thanks for downloading my application.

This Python program allows you to run code on two separate machines, a host and client, allowing the
client to view files on host machine, request files from host, or store files on host.

FTP_server.py is run on a host PC from the terminal/command line, setting it to a listening
state. FTP_client.py is run on a PC or mobile device also able to run Python in a terminal/command
line environment; validated on Linux PC and android mobile devices.



There are four valid commands:
- "view" which requests a list of stored files in hosts directory
  ex: "view"

- "send" which requests host to send a file to client to be stored in the clients current working directory
  ex: "send my_file.txt"

- "store" which sends a file to be stored in hosts chosen directory
  ex: "store my_file.jpg"

- "end" which terminates clients connection from host
  ex: "end"



To set up program:
#1 there are four locations in FTP_server.py where a file path will need to be added. These paths
  are prefaced by a comment and have the string 'file path goes here'. In these places, enter a string
  representing the desired working directory on host machine where you would like to send/receive files
  from/to.

  Note: The application is designed intentionally to only allow clients access to files in one location
  on host, but clients can specify file paths when storing files on host.

#2 the host application creates a log of connected clients and requested services in a file. A path to
  this file will need to be specified. Its location is specified in the log() function and needs to be added



Hope you enjoy the functionality. I'm a self-taught programmer, leave me a message with any issues you may
find or if you have any requests/modifications. 
