#!/usr/bin/env python3

from argparse import ArgumentParser
from threading import Thread
from time import ctime
import select
import socket
import sys


cli_socks = []


def serv(ip, port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((ip, port))

        s.listen(8)

        try:

            while True:

                print("\033[94m[*]\033[97m Waiting for connection...")

                cli_sock, cli_addr = s.accept()

                print("\033[92m[+]\033[97m Connection from: {0}".format(cli_addr))

                cli_socks.append(cli_sock)

                Thread(target=cli_handler, args=[cli_sock, cli_addr]).start()

        except KeyboardInterrupt:

            print("\033[93m[*]\033[97m Exiting...")

            exit()


def cli_handler(cli_sock, cli_addr):

    try:

        while True:

            try:

                data = cli_sock.recv(1024).decode('utf-8')

                if data:

                    msg = "@{0}: {1}".format(cli_addr[0], data)

                    for sock in cli_socks:

                        if sock is not cli_sock:

                            try:

                                sock.send(bytes(msg, 'utf-8'))

                            except BrokenPipeError:

                                print("\033[91m[!]\033[97m BrokenPipeError: {}".format(cli_addr))

                                try:

                                    sock.shutdown(socket.SHUT_RDWR)

                                    sock.close()

                                    if sock in cli_socks:

                                        cli_socks.remove(sock)

                                except OSError:

                                    print("\033[91m[!] OSError: {}".format(cli_addr))

                                    if sock in cli_socks:

                                        cli_socks.remove(sock)

            except ConnectionResetError:

                print("\033[91m[!]\033[97m ConnectionResetError: {}".format(cli_addr))

    except BrokenPipeError:

        cli_socks.remove(cli_sock)


def cli(ip, port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((ip, port))

        try:

            while True:

                readable, writable, errors = select.select([sys.stdin, s], [], [])

                for i in readable:

                    if i is s:

                        data = s.recv(1024).decode('utf-8')

                        print(data)

                    else:

                        msg = sys.stdin.readline().rstrip('\n')

                        s.send(bytes(msg, 'utf-8'))

        except (EOFError, KeyboardInterrupt):

            print("\033[93m[*]\033[97m Exiting...")

            s.shutdown(socket.SHUT_RDWR)

            s.close()

            exit()


def main():

    parser = ArgumentParser()

    parser.add_argument('-i', '--ip', default='localhost', required=False, )
    parser.add_argument('-p', '--port', type=int, default=54321, required=False, )
    parser.add_argument('-c', '--client', action='store_true', )
    parser.add_argument('-s', '--server', action='store_true', )

    args = parser.parse_args()

    if args.client:

        cli(args.ip, args.port)

    elif args.server:

        serv(args.ip, args.port)


if __name__ == '__main__':

    main()
