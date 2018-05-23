import serial
import argparse
import json
from flask import Flask


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--port', '-p', default='/dev/tty.usbmodem14322',
                    help='porta serial do embarcado')
parser.add_argument('--baudrate', '-b', default=115200, type=int,
                    help='baudrate da leitura serial')
parser.add_argument('--server-port', '-sp', default=8888, type=int,
                    help='porta do servidor (localhost:PORT)')


def clear_line(line):
    line = line.decode('utf-8')
    return line.split()


def parse(line):
    line = clear_line(line)
    return (int(line[1]), int(line[3]))


if __name__ == '__main__':
    args = parser.parse_args()
    app = Flask(__name__)

    with serial.Serial(args.port, args.baudrate) as ser:
        known_points = set()
        data = parse(ser.readline())
        while data[0] not in known_points:
            known_points.add(data[0])
            data = parse(ser.readline())

        n_points = len(known_points)
        data_buf = [None] * n_points

        @app.route('/')
        def home():
            data_buf = [None] * n_points
            for _ in range(n_points):
                data = parse(ser.readline())
                data_buf[data[0]] = data[1]

            if None in data_buf:
                raise ValueError('Valor nulo encontrado na leitura, falha de'
                                 + 'continuidade (leituras: {})'
                                 .format(data_buf))
            return json.dumps({'data': data_buf}), 200

        app.run(port=args.server_port)
