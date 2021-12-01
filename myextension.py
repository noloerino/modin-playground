import modin.pandas as pd
import time
import asyncio
from tornado import ioloop
from threading import Thread,Lock

# run this command in jupyter notebook to register the callbacks: %load_ext myextension

class VarWatcher(object):
    def __init__(self, ip):
        self.shell = ip
        self.stop_stats = False

    def pre_execute(self):
        self.stop_stats = True
        print("pre_execute")

    def pre_run_cell(self, info):
        print("pre_run_cell")

    def post_execute(self):
        def collect_stats(cell_num):
            while (not self.stop_stats):
                print(f"I'm a thread running cell {cell_num}!")
                time.sleep(2)
        user_vars = self.shell.ns_table['user_local']
        self.stop_stats = False
        print("deploying thread")
        stats_thread = Thread(target=collect_stats, args=(user_vars['cell_num'],))
        stats_thread.start()
        print("after deploying thread")

        ## TODO
        # create histogram

        # print the code in the cell
        # print('Cell code: "%s"' % result.info.raw_cell)

        # another way to access user variables
        # mydict = self.shell.user_ns


    def post_run_cell(self, result):
        print("post_run_cell")
        if result.error_before_exec:
            print('Error before execution: %s' % result.error_before_exec)
        

def load_ipython_extension(ip):
    vw = VarWatcher(ip)
    ip.events.register('pre_execute', vw.pre_execute)
    ip.events.register('pre_run_cell', vw.pre_run_cell)
    ip.events.register('post_execute', vw.post_execute)
    ip.events.register('post_run_cell', vw.post_run_cell)