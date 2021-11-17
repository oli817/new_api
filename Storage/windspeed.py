import datetime

from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Windspeed(Base):
    """ Windspeed """

    __tablename__ = "windspeed"

    sensor_id = Column(String(250), primary_key=True)
    address_id = Column(String(250), nullable=False)
    wind_speed = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, sensor_id, address_id, wind_speed, timestamp):
        self.sensor_id = sensor_id
        self.address_id = address_id
        self.timestamp = timestamp
        self.wind_speed = wind_speed
        self.date_created = datetime.datetime.now()


    def to_dict(self):
        dict = {}
        dict['sensor_id'] = self.sensor_id
        dict['address_id'] = self.address_id
        dict['wind_speed'] = self.wind_speed
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
