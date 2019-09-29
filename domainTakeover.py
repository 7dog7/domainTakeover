#!/usr/bin/python
# -*- coding:utf-8 -*-
import dns.resolver
import requests
import json
import re
import threading
import time
import inspect
import ctypes
from tld import get_tld
#tld,dnspython,requests
class ThreadPool:
    def __init__(self, size, timeout):
        self._size = size
        self._timeout = timeout

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid,
                                                         ctypes.py_object(
                                                             exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def _stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def start(self, func, task, data):
        record = dict()
        while len(task) or len(record) > 0: #任务必须有 记录线程
            while len(record) < self._size and len(task) > 0:
                item = task.pop()
                t = threading.Thread(target=func, args=(item, data,))
                t.start()
                record[t.getName()] = {'thread': t, 'time': time.time(),'data':item} #记录
            dellist = []
            for k, v in record.items():
                print('检测：' + k)
                if v['thread'].isAlive():
                    if time.time() - v['time'] > self._timeout:
                        self._stop_thread(v['thread'])
                        dellist.append(k)
                else:
                    dellist.append(k)
            time.sleep(1)
            for dl in dellist:
                del (record[dl])

def takeover(domain):
    n = 0
    if domain:
        domain = "http://" + domain[:-1]
        url = get_tld(domain, as_object=True)
        while True:
            try:
                r = requests.get(
                    'https://checkapi.aliyun.com/check/checkdomain?domain={0}&command=&token=Y3d83b57bc8aca0f156381976a6171f4a&ua=&currency=&site=&bid=&_csrf_token=&callback=jsonp_1569557125267_14652'.format(
                        url.fld), timeout=5).text
                if str(json.loads(re.match(".*?({.*}).*", r, re.S).group(1))['module'][0]['avail']) == '1':
                    return True
                else:
                    return False
            except Exception as e:
                print e
                n = n + 1
                if n >= 3:
                    break
                else:
                    continue

def main(domain, data):
    try:
        cn = dns.resolver.query(domain, 'CNAME')
        for list in cn.response.answer:
            for cname in list.items:
                judge = takeover(cname.to_text())
                if judge:
                    data.append(domain + "|" + str(judge))
                return judge
    except:
        return False

if __name__ == '__main__':
    f = open(r'domain.txt', 'rb')
    final_domain_list = []
    for line in f.readlines():
        final_domain = line.strip('\n')
        if final_domain.strip():
            final_domain_list.append(final_domain)
    data = []
    pool = ThreadPool(20, 300)
    pool.start(main, final_domain_list, data)
    if len(data) >0:
        with open(r'TakeoverResult.txt', 'ab+') as ff:
            for i in data:
                ff.write(i + '\n')
