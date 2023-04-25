import socket
from PIL import Image
import io

IMAGE_PATH = 'AZZ7719.jpg'

class Client:
    __slots__ = ["SERVER_IP", "SERVER_PORT", "socket"]
    def __init__(self, ip, port):
        self.SERVER_IP = ip
        self.SERVER_PORT = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, img):
        self.socket.connect((self.SERVER_IP, self.SERVER_PORT))

        # Load and convert the image into a byte stream
        byte_stream = io.BytesIO()
        img.save(byte_stream, format='JPEG')
        image_data = byte_stream.getvalue()

        # Send the image data
        self.socket.sendall(image_data)

        # Close the socket
        self.socket.close()
        
if __name__ == "__main__":
    client = Client("127.0.0.1", 3030)
    image = Image.open('AZZ7719.jpg')
    client.send(image)
