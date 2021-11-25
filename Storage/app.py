import connexion
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from temperature import Temperature
from windspeed import Windspeed
from base import Base
import yaml
import logging, logging.config
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
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
    app_config = yaml.safe_load(f.read())
    db_info = app_config["db"]
    
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s"% app_conf_file)
logger.info("Log Conf File: %s"% log_conf_file)

# with open("app_conf.yml", "r") as f:
#     app_config = yaml.safe_load(f.read())
#     db_info = app_config["db"]

# with open("log_conf.yml", "r") as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)
#     logger = logging.getLogger("basicLogger")

DB_ENGINE = create_engine("mysql+pymysql://%s:%s@%s:%s/%s"
                          % (db_info["user"], db_info["password"], db_info["hostname"], db_info["port"], db_info["db"]))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_outside_temperature_reading(timestamp, end_timestamp):
    """ Gets new blood pressure readings after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(Temperature).filter(and_(Temperature.date_created >= timestamp_datetime, Temperature.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Temperature readings after %s returns %d results" % (timestamp, len(results_list)))
    return results_list, 200


def get_wind_speed_reading(timestamp, end_timestamp):
    """ Gets new blood pressure readings after the timestamp """
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    readings = session.query(Windspeed).filter(and_(Windspeed.date_created >= timestamp_datetime, Windspeed.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Wind speed readings after %s returns %d results" % (timestamp, len(results_list)))
    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])

    count = app_config["count"]["count"]
    max_count = app_config["count"]["max_count"]
    while count < max_count:
        logger.info("Connecting to Kafka. It's" + str(count) + "attenps.")
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.info("Connection failed.")
            time.sleep(app_config["count"]["sleep"])
            count = count + 1
    
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    # This is blocking -it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]

        if msg["type"] == "ot": # Change this to your event type
            session = DB_SESSION()
            ot = Temperature(payload['sensor_id'],
                             payload['address_id'],
                             payload['outside_temperature'],
                             payload['timestamp']
                             )
            session.add(ot)
            session.commit()
            session.close()
            logger.info("Connecting to DB. Hostname: %s , Port: %d" % (db_info["hostname"], db_info["port"]))
        elif msg["type"] == "ws": # Change this to your event type
            session = DB_SESSION()

            ws = Windspeed(payload['sensor_id'],
                           payload['address_id'],
                           payload['wind_speed'],
                           payload['timestamp']
                           )
            session.add(ws)
            session.commit()
            session.close()
            logger.info("Connecting to DB. Hostname: %s , Port: %d" % (db_info["hostname"], db_info["port"]))

        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("oli817-weather-1.0.0-swagger.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)

