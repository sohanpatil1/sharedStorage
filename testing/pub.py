import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("receiver")  # Subscribe to the topic
    else:
        print(f"Connection failed with code {rc}")

def on_publish(client, userdata, mid, _, properties):
    print("Message published correctly")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
# client.on_publish = on_publish
client.on_message = on_message

client.connect("localhost", 1883, 60)

topic = "receiver"
message = "Hello, MQTT!"

client.publish("e465213b-e983-4124-a7be-036c08747962", message)
print(f"Message sent: {message}")
