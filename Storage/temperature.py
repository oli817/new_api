import datetime

from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Temperature(Base):
    """ Temperature """

    __tablename__ = "temperature"

    sensor_id = Column(String(250), primary_key=True)
    address_id = Column(String(250), nullable=False)
    outside_temperature = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, sensor_id, address_id, outside_temperature, timestamp):
        self.sensor_id = sensor_id
        self.address_id = address_id
        self.timestamp = timestamp
        self.outside_temperature = outside_temperature
        self.date_created = datetime.datetime.now()


    def to_dict(self):
        dict = {}
        dict['sensor_id'] = self.sensor_id
        dict['address_id'] = self.address_id
        dict['outside_temperature'] = self.outside_temperature
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
