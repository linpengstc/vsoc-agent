# -*- coding:utf-8 -*-

from rpc.nmap import nmap_pb2
from db.db import DB
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
import time
import hashlib


class NmapServicer(nmap_pb2.NmapScannerServicer):

    def getTaskStatus(self, request, context):
        db = DB()
        scanning = db.Nmap.count({"status": 0})
        finishing = db.Nmap.count({"status":1})
        if scanning == 0 and finishing == 0:
            # 如果没有结果的话或者结果为2,表示需要扫描
            return nmap_pb2.StatusResponse(status=nmap_pb2.StatusResponse.INIT)
        if scanning !=0:
            # 如果status为1,说明正在执行
            return nmap_pb2.StatusResponse(status=nmap_pb2.StatusResponse.RUNNING)
        if finishing !=0:
            # 如果status为2,说明还没有返回结果
            return nmap_pb2.StatusResponse(status=nmap_pb2.StatusResponse.ENDING)

    def scan(self, request, context):
        ips = request.ips
        db = DB()
        for ip in ips:
            db.Nmap.insert( {"target": ip, "status": 0 })
            print(ip)
        for ip in ips:
            self.do_scan(str(ip))
        return nmap_pb2.ScanResponse(result="success")

    def do_scan(self, target, options="-A -n -Pn -p0-65535"):
        # 记录结果
        db = DB()
        """
        nmproc = NmapProcess(target, options)
        nmproc.run_background()
        while nmproc.is_running():
            print("Nmap Scan running: ETC: {0} DONE: {1}%".format(nmproc.etc, nmproc.progress))
            time.sleep(2)
        print("rc: {0} output: {1}".format(nmproc.rc, nmproc.summary))
        """
        try:
            # 创建文件名
            md5 = hashlib.md5()
            md5.update(target)
            hash = md5.hexdigest()
            # with(open("data/nmap/" + hash + ".xml", "w")) as f:
            #     f.write(nmproc.stdout)
        except NmapParserException as e:
            print("Exception raised while parsing scan: {0}".format(e.msg))
        # 扫描完成,解析结果
        print {"status": 1, "result": hash }
        db.Nmap.update_one({"target": target}, {"$set": {"status": 1, "result": hash }})

    def getResult(self, request, context):
        db = DB()
        nmap_results = []
        statuses = db.Nmap.find({})
        for status in statuses:
            # 做更多的事情
            filename = "data/nmap/" + status['result']+ ".xml"
            print("[+] parse file: " + filename)
            with open(filename) as f:
                report = f.read()
            # nmap_results.append(nmap_pb2.NmapResult(target=status['result'], report=report))
            db.Nmap.remove({"target": status['target']})
            yield nmap_pb2.NmapResult(target=status['result'], report=report)
        # return nmap_pb2.ResultResponse(results = nmap_results)
