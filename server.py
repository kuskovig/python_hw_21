import socket
import re
from http import HTTPStatus

HOST = "127.0.0.1"
PORT = 9090

with socket.socket() as s:

    print(f"Binding server on {HOST}:{PORT}")
    try:
        s.bind((HOST, PORT))
    except socket.error as error_msg:
        print(f"Got error {error_msg} while binding port and host")

    s.listen()
    connection, address = s.accept()

    with connection:
        while connection:
            try:
                data = connection.recv(1024)
            except socket.error as msg:
                print(f"Server is closing due to error = {msg}")
                s.close()
                break

            if not data or data == b"close":
                print("Got termination signal", data, "and closed connection")
                break

            data_list = re.split(r'\r\n|\r|\n', data.decode("utf-8"))
            request_source = address
            request_method = data_list[0].split(" ")[0]
            status = data_list[0].split(" ")[1]
            try:
                status_code = int(re.search(r"(\/\?status=)(\d{1,3})$", status).group(2))
                try:
                    response_status = f"{HTTPStatus(status_code).value} {HTTPStatus(status_code).phrase}"
                except ValueError:
                    response_status = "200 OK"
            except AttributeError:
                response_status = "200 OK"
            headers = "\n".join([i for i in data_list[1:data_list.index("")]])

            connection.send(f"HTTP/1.1 {response_status}\n{headers}\n\n"
                            f"<p>Request Method:</p><pre>{request_method}</pre>"
                            f"<p>Request Source:<p><pre>{address}</pre>"
                            f"<p>Response Status:</p><pre>{response_status}</pre>"
                            f"<p>Headers:</p><pre>{headers}</pre>".encode("utf-8"))
            connection.close()