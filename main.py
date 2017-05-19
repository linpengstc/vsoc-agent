# -*- coding:utf-8 -*-

import grpc
from concurrent import futures
from rpc.nmap import nmap_pb2
from nmaptask.nmap_scanner import NmapServicer

import time

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nmap_pb2.add_NmapScannerServicer_to_server(NmapServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        print("停止RPC服务器")
        server.stop(0)


if __name__ == "__main__":
    serve()