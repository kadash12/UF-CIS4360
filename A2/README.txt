Johnny Li
Assignment 2 

		Unencrypted P2P Instant Messenger Instruction
Project Summary: A simple unencrypted instant messenger using TCP to send messages between hosts the program
should read from standard input and send all input data to the other instance of your application (running on the 
other host), via TCP/IP over a network port, which should default to port 9999 unless you provide a different 
port number at runtime.

Content:
UnencryptedIM.cpp
Makefile
README

1. Run the makefile, this should make an executable program. 

2. Run server through:
	./UnencryptedIM -s <port>
		or
To use the default port:
	./UnencryptedIM -s 

3. Run client through:
	./UnencryptedIM -c <hostname> <port>
		or
To use the default port:
	./UnencryptedIM -c <hostname>

4. Send messages, press enter to check on receiver message if order is broken.

Note: There is a queue of 5 messages and each message has a max length of 1024 byte. The order of sending a message is
as such: 
S M	->	C
S 	<-	M C
Repeat
This produced the expected response of the program through threading however since the select() was not implemented successfully,
the order can be broken as such
S M	->	C	//Client will only recieve the first message.
S M	->	C	//Press enter to recieve the second message.
	or
S 	<-	M C	//Server will only recieve the first message.
S 	<-	M C	//Press enter to recieve the second message
