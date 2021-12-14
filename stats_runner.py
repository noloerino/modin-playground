import time
import asyncio
from tornado import ioloop
from threading import Thread,Lock

# run this command in jupyter notebook to register the callbacks: %load_ext stats_runner

_verbose = False

class StatsRunner(object):
    def __init__(self, ip):
        self.shell = ip
        self.stop_stats = False

    def _log(self, *args):
        if _verbose:
            print(*args)

    def pre_execute(self):
        # print("pre_execute")
        self.stop_stats = True

    def pre_run_cell(self, info):
        # print("pre_run_cell")
        pass

    def post_execute(self):
        # print("post_execute")
        pass
        # print the code in the cell
        # print('Cell code: "%s"' % result.info.raw_cell)

        # another way to access user variables
        # mydict = self.shell.user_ns


    def post_run_cell(self, result):
        # print("post_run_cell")
        if result.error_before_exec:
            print('Error before execution: %s' % result.error_before_exec)
            return
        # PROBLEM: it seems like in some circumstances, time.sleep(0) will
        # cause the thread to be slept when self.stop_stats is True, but then resume
        # when the next stats collection thread is spawned
        # since stats_manager should be thread-safe, it shouldn't be an issue, but
        # may cause confusing behavior
        def collect_stats(cell_num):
            import modin
            if "+" in modin.__version__:
                from modin.core.storage_formats.pandas import stats_manager
                self._log("starting stats collection thread, stop_stats=", self.stop_stats)
                i = 0
                while (not self.stop_stats) and stats_manager.has_next():
                    self._log("computing next...", i, "of", stats_manager.size())
                    stats_manager.compute_next()
                    self._log("compute done", i)
                    i += 1
                    time.sleep(2) # yield thread: https://stackoverflow.com/questions/787803/
                if stats_manager.has_next():
                     self._log("interrupted before finishing yay (finished iter)", i)
                else:
                     self._log("ran out of stats to compute")
                self._log("current stats:", stats_manager.get_all())
        # user_vars = self.shell.ns_table['user_local']
        self.stop_stats = False
        # print("deploying thread")
        stats_thread = Thread(target=collect_stats, args=(None,))
        # stats_thread = Thread(target=collect_stats, args=(user_vars['cell_num'],))
        stats_thread.start()
        # print("after deploying thread")
        

def load_ipython_extension(ip):
    vw = StatsRunner(ip)
    ip.events.register('pre_execute', vw.pre_execute)
    ip.events.register('pre_run_cell', vw.pre_run_cell)
    ip.events.register('post_execute', vw.post_execute)
    ip.events.register('post_run_cell', vw.post_run_cell)
