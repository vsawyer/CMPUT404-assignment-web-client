#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port
        if port == None:
            port = 80    
        path = parsed.path
        return host, port, path    

    def connect(self, host, port):
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print('Failed to create socket!')
            print('Error code: ' + str(msg[0]) + ', error message ' + msg[1])
            sys.exit()
        s.connect((host, int(port)))
        return s

    def get_code(self, data):
        code = int(data.split()[1])
        return code

    def get_headers(self,data):
        response = data.split("\r\n\r\n")
        header = response[0]
        return header

    def get_body(self, data):
        response = data.split("\r\n\r\n")
        body = response[1]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        host, port, path = self.get_host_port(url)
        s = self.connect(host, port)
        request = "GET %s HTTP/1.1\r\n" \
            "Host: %s\r\n" \
            "Connection: close\r\n" \
            "Accept: */*\r\n\r\n" % (path, host)        
        try:
            s.sendall(request.encode("UTF8"))
        except socket.error:
            print('Send failed!')
            sys.exit()
            s.close()
        reply = self.recvall(s)
        s.close()
        return HTTPRequest(self.get_code(reply), self.get_body(reply))

    def POST(self, url, args=None):
        host, port, path = self.get_host_port(url)
        if args is not None:
            content = urllib.urlencode(args)
            contentLength = len(content)
        else:
            contentLength = 0
            content = ""
        s = self.connect(host, port)
        request = "POST %s HTTP/1.1\r\n" \
            "Host: %s\r\n" \
            "Connection: close\r\n" \
            "Content-Type: application/x-www-form-urlencoded\r\n" \
            "Accept: */*\r\n" \
            "Content-Length: %s\r\n\r\n" % (path, host, contentLength) + content
        try:
            s.sendall(request.encode("UTF8"))
        except socket.error:
            print('Send failed!')
            sys.exit()
            s.close()      
        reply = self.recvall(s)
        s.close()
        return HTTPRequest(self.get_code(reply), self.get_body(reply))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    
