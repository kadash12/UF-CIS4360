/*
 * Title: UnencryptedIM.cpp
 * Project Summary: A simple unencrypted instant messenger using TCP to send messages between hosts.
 * program should read from standard input and send all input data to the other instance of your application
 * (running on the other host), via TCP/IP over a network port, which should default to port 9999 unless you
 * provide a different port number at runtime.
 *
 * @author: Johnny Li
 * CIS4360: Computer and Information Security
 * Version: No select();
 */
//Libraries
#include <iostream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <cstdlib>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

using namespace std;

//Global variables
int port = 9999;	//Default port
struct hostent *hostname;	//Host name for client
string letter;      //Program letter s or c
string msg;         //Message

/*
 * Following command-line options:	UnencryptedIM -s <portnum> |-c hostname <portnum>
 */
int main(int argc, char* argv[]) {
    letter = argv[1];   //Get letter

	//Check number of arguments and letter.
	if((argc >= 2) && (letter.compare("-s") == 0)) {		//argc = 2+ and -s --> server
	    //Get port if any
		if(argc == 3){
		    port = atoi(argv[2]);	//Convert argument to int.
		}
		//------------------------------------------------------------------
		//https://www.geeksforgeeks.org/socket-programming-cc/
		//Initalize socket
        int server, socketn, readnum;
        struct sockaddr_in address;
        int one = 1;
        int addrlen = sizeof(address);
        char buf[1024] = {0};	//Message buffer

        //Creating socket file descriptor
        server = socket(AF_INET, SOCK_STREAM, 0);

        //Forcefully attaching socket
        setsockopt(server, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &one, sizeof(one));

		//Initalize addresses
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(port);
        //Forcefully attaching socket to the port
        bind(server, (struct sockaddr *)&address, sizeof(address));

		//Listen for socket.
        listen(server, 5);

		//Accept new socket connection.
        socketn = accept(server, (struct sockaddr *)&address, (socklen_t*)&addrlen);

		while(true){
			msg.clear();
			//Create message
			//https://stackoverflow.com/questions/347949/how-to-convert-a-stdstring-to-const-char-or-char
			getline(cin, msg);
			if(msg != ""){
				char * m = new char[msg.size() + 1];
				copy(msg.begin(), msg.end(), m);
				m[msg.size()] = '\0';       //Terminating 0

				send(socketn , m, (int)strlen(m), 0);	//Send message
				delete[] m;
			}
			else{
				send(socketn, " ", 1, 0);
			}
			bzero(buf,1024);		//Clear buffer

			read(socketn, buf, 1024);	//Get message
			printf("%s \n",buf);
        }
        //------------------------------------------------------------------
	}
	else if ((argc >= 3) && (letter.compare("-c")==0)) {  //argc = 3+ and -c --> client
        //Get port if any
		if(argc == 4){
		    port = atoi(argv[3]);	//Convert argument to int.
		}
        //------------------------------------------------------------------
		//https://www.geeksforgeeks.org/socket-programming-cc/
		//Initalize socket
        int sock = 0, readnum;
        struct sockaddr_in serv_addr;
        char buf[1024] = {0};	//Message buffer

		sock = socket(AF_INET, SOCK_STREAM, 0);

		//Initalize addresses
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(port);
        //Convert IPv4 and IPv6 addresses from text to binary form
		//inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);		//For testing on localhost

		//http://www.linuxhowtos.org/C_C++/socket.htm
		hostname = gethostbyname(argv[2]);     //Get hostname
		bcopy((char *)hostname->h_addr, (char *)&serv_addr.sin_addr.s_addr, hostname->h_length);

		//Connect socket
		connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

		while(true){
			bzero(buf,1024);	//Clear buffer

			read( sock, buf, 1024);	//Get message
			printf("%s \n",buf );

			msg.clear();
			//Create message
			//https://stackoverflow.com/questions/347949/how-to-convert-a-stdstring-to-const-char-or-char
			getline(cin, msg);
			if(msg != ""){
				char * m = new char[msg.size() + 1];
				copy(msg.begin(), msg.end(), m);
				m[msg.size()] = '\0';       //Terminating 0

				send(sock, m, (int)strlen(m), 0); 	//Send message
				delete[] m;
			}
			else{
				send(sock, " ", 1, 0);
			}
        }
        //------------------------------------------------------------------
    }
    else {				//Incorrect command line argument
		return 0;		//Exit program
	}
}
