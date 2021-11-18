import connexion
from connexion import NoContent
import logging,logging.config
import json
import datetime
from pykafka import KafkaClient
import yaml
import requests
import time
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    a_config = yaml.safe_load(f.read())
    app_config = a_config["events"]
    
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s"% app_conf_file)
logger.info("Log Conf File: %s"% log_conf_file)


# with open('app_conf.yml', 'r') as f:
#     a_config = yaml.safe_load(f.read())
#     app_config = a_config["events"]


# with open('log_conf.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)
#     logger = logging.getLogger('basicLogger')

count = a_config["count"]["count"]
max_count = a_config["count"]["max_count"]
while count < max_count:
    logger.info("Connecting to Kafka. It's" + str(count) + "attenps.")
    try:
        client = KafkaClient(hosts='acit4850-lab6.eastus2.cloudapp.azure.com:9092')
        topic = client.topics[str.encode(a_config["events"]["topic"])]
        break
    except:
        logger.info("Connection failed.")
        time.sleep(a_config["count"]["sleep"])
        count = count + 1

def report_outside_temperature_reading(body):

    # logger.info("Received event %s request with a unique id of %s"
    #             % ("read temperature", body["sensor_id"]))
    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config["temperature"]["url"], json=body, headers=headers)
    # logger.info("Returned event %s response %s with status %s"
    #             % ("read temperature", body["sensor_id"], response.status_code))
    # client = KafkaClient(hosts='acit4850-lab6.eastus2.cloudapp.azure.com:9092')
    # topic = client.topics[str.encode(app_config["topic"])]


    producer = topic.get_sync_producer()
    msg = {"type": "ot",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201

def report_wind_speed_reading(body):
    # logger.info("Received event %s request with a unique id of %s"
    #             % ("read wind speed", body["sensor_id"]))
    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config["wind_speed"]["url"], json=body, headers=headers)
    # logger.info("Returned event %s response %s with status %s"
    #             % ("read wind speed", body["sensor_id"], response.status_code))

    # client = KafkaClient(hosts='app_config["hostname"]:app_config["port"]')
    # client = KafkaClient(hosts='acit4850-lab6.eastus2.cloudapp.azure.com:9092')
    # topic = client.topics[str.encode(app_config["topic"])]

    producer = topic.get_sync_producer()

    msg = {"type": "ws",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return NoContent, 201


# def log_json(logs):
#     final_logs = json.dumps(logs, indent=4)
#     with open(EVENTS_FILE, 'w') as file:
#         file.write(final_logs)





app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("oli817-weather-1.0.0-swagger.yaml",
            strict_validation=True,
            validate_responses=True)





if __name__ == "__main__":
    app.run(port=8080)

