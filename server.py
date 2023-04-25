import socket
from PIL import Image
import io
OUTPUT_IMAGE_PATH = 'received_image.jpg'
class Server:
    __slots__ = ["SERVER_IP", "SERVER_PORT", "socket"]
    def __init__(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.SERVER_IP, self.SERVER_PORT))
        self.socket.listen(1)
    
    def run(self):
        while True:
            connection, client_address = self.socket.accept()
            try:
                # Receive the image data
                image_data = b''
                while True:
                    data = connection.recv(4096)
                    if not data:
                        break
                    image_data += data
                # Convert the byte stream to an image and save it
                byte_stream = io.BytesIO(image_data)
                image = Image.open(byte_stream)
                image.save(OUTPUT_IMAGE_PATH)
            finally:
                # Clean up the connection
                connection.close()

if __name__ == "__main__":
    server = Server("127.0.0.1", 3030)
    server.run()