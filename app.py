from __init__ import *
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), create_app(), keyfile='key.pem',certfile='cert.pem')
    http_server.serve_forever()










