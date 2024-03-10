import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed with code {rc}")

def on_publish(client, userdata, mid, _, s):
    print("Message published correctly")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_publish = on_publish
client.connect("localhost", 1883, 60)

topic = "receiver"
message = "Hello, MQTT!"

while True:
    client.publish(topic, message)
    print(f"Message sent: {message}")
    time.sleep(1)
