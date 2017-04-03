import socket
import os
import sys


class Server:
	""" Simple HTTP Server implementation """
	
	def __init__(self, port=8000):
		""" Initializing Server object """
		self.host = "localhost"
		self.port = port
		
	def start_server(self):
		""" Trying to acquire socket and launch server """
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			print("Starting http server on ", self.host, ":", self.port)
			self.socket.bind((self.host, self.port))
		except Exception as e:
			print ("Warning: Exception occured", e)
			self.socket.close()
		print("[+] Server started")
		self._requests_handler()
        
	@staticmethod
	def check_for_index(req_path):
		""" Looking for 'index.html' file in directory. Returns True 
		if current folder contains index file """
		result = False
		for item in os.listdir(req_path):
			if item == "index.html":
				result = True
				break
		return result
        
	@staticmethod
	def open_file(req_path, conn):
		""" Sends objects of 'file' type to browser """
		connection = conn
		connection.send("HTTP/1.0 200 OK\r\n".encode("utf-8"))
		connection.send("Connection: close\r\n".encode("utf-8"))
		with open(req_path, "rb") as file_:
			data = file_.read()
		connection.send("Content-Length: {}\r\n".format(len(data)).encode("utf-8"))
		connection.send("\r\n".encode("utf-8"))
		connection.send(data)
        
	@staticmethod
	def redirect(conn, path):
		""" Simple http redirect """
		connection = conn
		connection.send("HTTP/1.0 301 Moved Permanently\r\n".encode("utf-8"))
		connection.send("Location: {}\r\n".format(path).encode("utf-8"))
		connection.send("Refresh: 0; url={}\r\n".format(path).encode("utf-8"))
		connection.send("Connection: close\r\n".encode("utf-8"))
		connection.send("\r\n".encode("utf-8"))
		connection.send("<html>\r\n".encode("utf-8"))
		connection.send("<head><meta http-equiv=\"Refresh\" content=\"0; url={}\" /></head>\r\n".format(path).encode("utf-8"))
		connection.send("<body><p>Please follow <a href=\"{}\">this link</a>.</p></body>\r\n".format(path).encode("utf-8"))
		connection.send("</html>".encode("utf-8"))
        
	@staticmethod
	def build_directory(req_path, conn):
		""" Builds folder view with all contained files and folders 
		and sends it to browser """
		connection = conn
		if Server.check_for_index(req_path):
			req_path += "/index.html"
			connection = Server.open_file(req_path, connection)
		else:
			connection.send("HTTP/1.0 200 OK\r\n".encode("utf-8"))
			connection.send("Connection: close\r\n".encode("utf-8"))
			connection.send("\r\n".encode("utf-8"))
			connection.send("<html><head><title>Directory Listing</title></head><body><h1>Directory Listing</h1><ul>".encode("utf-8"))
			if req_path != ".":
				connection.send(
				("<li><a href=\"" + "/".join(req_path.split("/")[:-1]) + "\">..</a></li>\r\n").encode("utf-8"))
			for item in os.listdir(req_path):
				connection.send(("<li><a href=\"" + req_path + "/" + item + "\">" + item + "</a></li>\r\n").encode("utf-8"))
			connection.send("</ul></body></html>".encode("utf-8"))

	def _requests_handler(self):
		""" Handles all requests coming to server """
		while True:
			self.socket.listen(0)
			conn, addr = self.socket.accept()
			req = str(conn.recv(8192))
			req_path = "." + req.splitlines()[0].split(" ")[1]
			print("[i] Request: " + req_path)
			if os.path.isdir(req_path):
				if req_path.endswith("/"):
					req_path = req_path[:-1]
					self.build_directory(req_path, conn)
				else:
					self.redirect(conn, req_path + "/")
			elif os.path.isfile(req_path):
				self.open_file(req_path, conn)
			else:
				conn.send("HTTP/1.0 404 Not Found\r\n".encode("utf-8"))
				conn.send("Connection: close\r\n".encode("utf-8"))
				conn.send("\r\n".encode("utf-8"))
				conn.send("<html><head><title>Not Found</title></head><body><h1>Not Found</h1></body></html>".encode("utf-8"))
			conn.close()

if __name__ == "__main__":
	try:
		port = sys.argv[1]
		s = Server(int(port))
	except Exception as e:
		print("Invalid argument or no argument specified. Starting server on 8000 port", e)
		s = Server()
	s.start_server()
	
	
