import socket
import ssl
import threading
import logging
import socks
LOCAL_HOST = '192.168.15.77'
LOCAL_PORT = 8443
SOCKS_HOST = '192.168.15.77'
SOCKS_PORT = 1080
REMOTE_HOST = 'g.whatsapp.net'
REMOTE_PORT = 5222
logging.basicConfig(level=logging.ERROR)
def handle_proxy(conn1,conn2):
    try:
        while True:
            data = conn1.recv(4096)
            if not data:
                break
            logging.debug(str([data]))
            # Process the data as needed
            processed_data = data

            # Send the processed data back to the client
            conn2.sendall(processed_data)
    except Exception as e:
        logging.exception("Error occurred while processing client data:")
    finally:
        conn1.close()
        conn2.close()
def handle_client(conn1):
    try:
# Create a new connection to the SOCKS proxy
        conn2 = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        conn2.set_proxy(socks.SOCKS5, SOCKS_HOST, SOCKS_PORT)
        conn2.settimeout(60)
        # proxy_socket = ssl.wrap_socket(proxy_socket, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1_2)
        conn2.connect((REMOTE_HOST, REMOTE_PORT))
        t1 = threading.Thread(target=handle_proxy, args=(conn1,conn2),daemon=True)
        t2 = threading.Thread(target=handle_proxy, args=(conn2,conn1),daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except Exception as e:

        logging.exception("Error occurred while processing client data:")
    finally:
        conn1.close()
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
def accept_clients(sock):
    while True:
        try:
            conn, addr = sock.accept()
            # conn = context.wrap_socket(conn, server_side=True)
            threading.Thread(target=handle_client, args=(conn,),daemon=True).start()
        except KeyboardInterrupt:
            return
        except:
            logging.exception("")


def start_server():
    backlog = 5
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((LOCAL_HOST, LOCAL_PORT))
    server_sock.listen(backlog)
    logging.debug(f'Starting SSL TCP proxy server on {LOCAL_HOST}:{LOCAL_PORT}')
    accept_clients(server_sock)

if __name__ == '__main__':
    start_server()
