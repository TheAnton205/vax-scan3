import boto3 #for connecting with the s3 bucket
from botocore.config import Config #for configuring the service

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json

text1 = []

ENDPOINT = "EDNPOINT"
CLIENT_ID = "testDevice"
PATH_TO_CERT = "CERT_"
PATH_TO_KEY = "PRIVEATEKEY"
PATH_TO_ROOT = "certificates/root.pem"
MESSAGE = "Hello World"
TOPIC = "IOTDEVICE/blink"
RANGE = 1


my_config = Config(
    region_name = 'us-east-2',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

def blink():
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                endpoint=ENDPOINT,
                cert_filepath=PATH_TO_CERT,
                pri_key_filepath=PATH_TO_KEY,
                client_bootstrap=client_bootstrap,
                ca_filepath=PATH_TO_ROOT,
                client_id=CLIENT_ID,
                clean_session=False,
                keep_alive_secs=6
                )
    print("Connecting to {} with client ID '{}'...".format(
            ENDPOINT, CLIENT_ID))
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")
    # Publish message to server desired number of times.
    print('Begin Publish')
    for i in range (RANGE):
        data = "{} [{}]".format(MESSAGE, i+1)
        message = {"message" : data}
        mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
        print("Blinks on!")
        t.sleep(3)
        mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
        print("Blinks off!")
        t.sleep(0.1)
        
    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    
def detect_text(photo, bucket):

    client=boto3.client('rekognition', config=my_config)

    response=client.detect_text(Image={'S3Object':{'Bucket':'vax-scan','Name':'image1827600.png'}})
                        
    textDetections=response['TextDetections']
    print ('Detected text\n----------')
    for text in textDetections:
            print ('Detected text:' + text['DetectedText'])
            text1.append(text['DetectedText'])
            print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
            print ('Id: {}'.format(text['Id']))
            if 'ParentId' in text:
                print ('Parent Id: {}'.format(text['ParentId']))
            print ('Type:' + text['Type'])
            print()
    return len(textDetections)

def check_card():
#    text1 = ['information', 'Covid', 'hello', 'test']
    test_words = ['information', 'mm', 'incluye', 'de', 'vaccines', 'Date']
    if(set(test_words).issubset(text1)):
        print("yes!")
        nameIndex = text1.index('Last')
        nameIndex = nameIndex - 1
        print("Name = " + text1[nameIndex] + " passed!")
        blink()

    else:
        print("NOT ALLOWED!")


def main():

    bucket='vax-scan'
    photo='image1827600.png'
    text_count=detect_text(photo,bucket)
    print("Text detected: " + str(text_count))
    print(text1)

    check_card()


if __name__ == "__main__":
    main()
