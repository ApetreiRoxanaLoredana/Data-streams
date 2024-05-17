from flask import Flask, render_template, Response, request
from pykafka import KafkaClient
from pykafka.common import OffsetType


def get_kafka_client():
    return KafkaClient(hosts='127.0.0.1:9092')


app = Flask(__name__)


@app.route('/')
def index():
    return (render_template('index.html'))


@app.route('/topic/<topic_name>')
def get_message(topic_name):
    client = get_kafka_client()

    def events():
        for i in client.topics[topic_name].get_simple_consumer(auto_offset_reset=OffsetType.LATEST, reset_offset_on_start=True):
            yield 'data:{0}\n\n'.format(i.value.decode())

    return Response(events(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
