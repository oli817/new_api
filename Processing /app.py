import json
import connexion
from connexion import NoContent

import logging
import logging.config
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import os


with open("app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f.read())
    data_file = app_config['datastore']['filename']

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_stats():
    logger.info('Get stats request started')

    if os.path.isfile('data.json'):
        with open(app_config['datastore']['filename']) as f:
            logger.info('Request has ended')
            return json.load(f), 200
    else:
        logger.error('file does not exist')
        msg = 'file does not exist'
        return msg, 404

def populate_stats():
    """ Periodically update stats """
    logger.info("Request Started")
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(data_file, "r") as f:
        last_update = json.load(f)["last_updated"]

    response_temperature = requests.get(app_config["temperature"]["url"], params={'timestamp': last_update})
    response_wind_speed = requests.get(app_config["wind_speed"]["url"], params={'timestamp': last_update})

    # if response_temperature.status_code == 200 and response_wind_speed.status_code == 200:

    if len(response_temperature.json()) != 0 and len(response_wind_speed.json()) != 0 :
        temp_list = []
        for temp in response_temperature.json():
            temp_list.append(temp['outside_temperature'])
        max_tem_reading = max(temp_list)
        num_tem_reading = len(response_temperature.json())

        wind_speed_list = []
        for wind_speed in response_wind_speed.json():
            wind_speed_list.append(wind_speed['wind_speed'])
        max_ws_reading = max(wind_speed_list)
        num_ws_reading = len(response_wind_speed.json())

        data = json.dumps({
            "num_tem_reading": num_tem_reading,
            "max_tem_reading": max_tem_reading,
            "num_ws_reading": num_ws_reading,
            "max_ws_reading": max_ws_reading,
            "last_updated": dt_string
        })

        with open('data.json', 'w') as f:
            f.write(data)

        logger.debug(data)



def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval',seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("oli817-weather-1.0.0-swagger.yaml",
            strict_validation=True,
            validate_responses=True)



if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)

