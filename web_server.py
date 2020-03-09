from BaseHTTPServer import BaseHTTPRequestHandler

class GetHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        x = self.wfile.write
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # <--- HTML starts here --->
        x("<html>")
        # <--- HEAD starts here --->
        x("<head>")
        x("<title>Title goes here!</title>")
        x("</head>")
        # <--- HEAD ends here --->
        # <--- BODY starts here --->
        x("<body>")
        x("<p>This is a test.</p>")
        x("</body>")
        # <--- BODY ends here --->
        x("</html>")
        # <--- HTML ends here --->

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('10.0.10.10', 80), GetHandler)
    print 'Starting server, use <Ctrl + F2> to stop'
    server.serve_forever()