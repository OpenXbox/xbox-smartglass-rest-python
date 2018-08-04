from gevent import monkey
monkey.patch_all()
from gevent import wsgi

import argparse
from xbox.rest.engine.server import app

def main():
    parser = argparse.ArgumentParser(description="Xbox One SmartGlass REST server")
    parser.add_argument('--address', '-a', default='0.0.0.0',
                        help='IP address to bind to')
    parser.add_argument('--port', '-p', default=5557,
                        help='Port to bind to')

    args = parser.parse_args()

    server = wsgi.WSGIServer((args.address, args.port), app)
    print('Xbox Smartglass REST server started on {0}:{1}'.format(
        server.server_host, server.server_port
    ))
    server.serve_forever()

if __name__ == '__main__':
    main()
