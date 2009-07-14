import SocketServer
import SimpleHTTPServer

class HTTPServer:
    """
    Simple HTTP Server
    """
    def __init__(self,handler=None,port=8080):
        self.port = port
        self.handler = handler or DefaultHandler

    def run(self):
        self.server = SocketServer.ThreadingTCPServer(
                ('localhost', self.port), self.handler)
        print "serving at http://localhost:", self.port
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.shutdown()

class DefaultHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """
    The DefaultHandler serves up DataGrid results using native classes
    """
    def do_GET(self):
        if self.path=='/exit':
            exit()
        elif self.path=='/hello':
            self.request.send('Hello World!')
        else:
            # serve files, and directory listings by following self.path from
            # current working directory
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
