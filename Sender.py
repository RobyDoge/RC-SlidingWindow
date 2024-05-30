import random
import socket
import threading
import time

def getRandomNumber() -> int:
    return random.randint(1, 100)

class SlidingWindowSender:
    def __init__(self, host, port, window_size, timeout=5):
        self.host = host
        self.port = port
        self.window_size = window_size
        self.timeout = timeout
        self.lock = threading.Lock()
        self.ack:set = set()
    def send_element(self, element, ack_event):
        while not ack_event.is_set():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                try:
                    if getRandomNumber() < 10:
                        print(f"Oops! {element} lost in transmission...")
                        time.sleep(5)
                        continue
                    s.connect((self.host, self.port))
                    s.sendall(str(element).encode('utf-8'))
                    response = s.recv(1024).decode('utf-8')
                    if response != "ACK":
                        print(f"Oops! ACK not received for element {element}")
                        continue
                    print(f"Received response for element {element}: {response}")
                    ack_event.set()
                    self.ack.add(element)
                except socket.timeout:
                    print(f"Timeout for element {element}, resending...")
                except socket.error as e:
                    print(f"Socket error for element {element}: {e}")
                    break

    def send_window(self, elements):
        acks = [threading.Event() for _ in range(len(elements))]
        threads = []
        if self.ack.__contains__(elements[0]):
            return

        for i, element in enumerate(elements):
            thread = threading.Thread(target=self.send_element, args=(element, acks[i]))
            thread.start()
            threads.append(thread)
        
        # Wait for the first element in the window to get an ACK
        acks[0].wait()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def sliding_window(self, elements):
        i = 0
        while i < len(elements):
            window_elements = elements[i:i + self.window_size]
            print(f"Current window: {window_elements}")
            self.send_window(window_elements)
            i += 1  # Move the window one element to the right after receiving an ACK for the first element

# Example usage
if __name__ == "__main__":
    host = "localhost"
    port = 12345
    numberOfPackages = int(input("Enter the number of packages: "))
    window_size = int(input("Enter the window size: ")) 
    timeout = 5

    sender = SlidingWindowSender(host, port, window_size, timeout)
    sender.sliding_window([i for i in range(1, numberOfPackages + 1)])
