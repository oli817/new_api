import mysql.connector

db_conn = mysql.connector.connect(host="acit4850-lab6.eastus2.cloudapp.azure.com", user="root", password="password", database="events")
db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE temperature
          (id INTEGER NOT NULL AUTO_INCREMENT,
           sensor_id VARCHAR(250) NOT NULL, 
           address_id VARCHAR(250) NOT NULL,
           outside_temperature INTEGER NOT NULL,
           timestamp VARCHAR(250) NOT NULL,
           date_created VARCHAR(250) NOT NULL,
           CONSTRAINT temperature_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE windspeed
          (id INTEGER NOT NULL AUTO_INCREMENT,
           sensor_id VARCHAR(250) NOT NULL, 
           address_id VARCHAR(250) NOT NULL,
           wind_speed INTEGER NOT NULL,
           timestamp VARCHAR(250) NOT NULL,
           date_created VARCHAR(250) NOT NULL,
           CONSTRAINT wind_speed_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
