import logging

import gevent
from zerorpc import Pusher, Subscriber, Client, Puller

from .hub import Hub, Message


class SubscriberAPI():
    def __init__(self, client_ip):
        # Setup pusher service
        self.client = Client()
        self.client.connect(client_ip)

        # print(self.pusher.load_data("TEST"))

        # Connect to message hub
        self._hub = Hub()

        self._hub.subscribe(Message.LoadData, self.client.load_data, self)

    def data_loaded(self, data):
        import msgpack

        unpacked_data = msgpack.unpackb(data)

        self._hub.publish(Message.AddData, unpacked_data)

    def data_unloaded(self, data):
        pass

    def testing(self, msg):
        print("Received 'testing' call on subscriber")


def launch(server_ip=None, client_ip=None):
    logging.info("[client] Starting services...")

    server_ip = server_ip or "tcp://127.0.0.1:4242"
    client_ip = client_ip or "tcp://127.0.0.1:4243"

    # Setup the subscriber service
    sub_api = SubscriberAPI(client_ip)
    subscriber = Subscriber(sub_api)
    subscriber.bind(server_ip)

    gevent.spawn(subscriber.run)

    logging.info(
        "[client] Client is now sending on %s and listening on %s.",
        client_ip, server_ip)

    # Attempt testing whether fuction was added to server object
    sub_api.client.testing("This is a test on the server")
    sub_api.client.load_data_from_path('/home/nmearl/Downloads/Transcript.txt', '*')