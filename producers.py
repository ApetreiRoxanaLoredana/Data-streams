import time
from datetime import datetime
import uuid
import threading
import json
from pykafka import KafkaClient


# READ COORDINATES FROM GEOJSON
def read_coordinates(bus_file):
    with open(bus_file) as input_file:
        json_data = json.load(input_file)
        coordinates_list = []
        for feature in json_data['features']:
            coordinates = feature['geometry']['coordinates']
            time_bus = feature['properties']['time']
            coordinates_list.append({'longitude': coordinates[0], 'latitude': coordinates[1], 'time': time_bus})
        return coordinates_list


# GENERATE UUID
def generate_uuid():
    return uuid.uuid4()


# KAFKA PRODUCER FUNCTION
def kafka_producer(busline, coordinates, sleep_time):
    client = KafkaClient("localhost:9092")
    topic = client.topics['geodata_final']
    producer = topic.get_sync_producer()

    data = {'busline': busline}

    i = 0
    while i < len(coordinates):
        data['key'] = data['busline'] + '_' + str(generate_uuid())
        data['timestamp'] = str(datetime.utcnow())
        data['latitude'] = coordinates[i]['latitude']
        data['longitude'] = coordinates[i]['longitude']
        data['time'] = coordinates[i]['time']
        message = json.dumps(data)
        print(message)
        producer.produce(message.encode('ascii'))
        time.sleep(sleep_time)
        i += 1


# FUNCTION TO RUN KAFKA PRODUCER IN THREAD
def run_kafka_producer(busline, coordinates, sleep_time):
    thread = threading.Thread(target=kafka_producer, args=(busline, coordinates, sleep_time))
    thread.start()


# MAIN FUNCTION
def main():
    bus_lines = {
        '24B': './data/24B.json',
        '25': './data/25.json',
        '5': './data/5.json'
    }
    sleep_times = [2, 0.75, 1.5]
    for busline, bus_file in list(bus_lines.items())[:3]:
        coordinates = read_coordinates(bus_file)
        sleep_time = sleep_times.pop(0)
        run_kafka_producer(busline, coordinates, sleep_time)


if __name__ == "__main__":
    main()
