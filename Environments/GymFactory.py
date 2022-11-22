import threading
import traceback

from Environments import SkyRunner
from threading import Thread
import queue

exit_flag = 0
q = queue.Queue()
r = queue.Queue()
q_lock = threading.Lock()
r_lock = threading.Lock()


class Factory:
    def __init__(self, env_int=5, thread_int=5):
        super().__init__()
        global q
        global r
        self.threads = []
        for i in range(env_int):
            env = SkyRunner.CustomEnv()
            q.put(env)
        for j in range(thread_int):
            self.threads.append(Worker(j, "Reloader"))

    def get_ready(self):
        global r
        obs, env = r.get(block=True)
        return obs, env

    def queue_done(self, done_env):
        global q
        q.put(done_env)

    def run(self):
        for t in self.threads:
            t.start()

    def stop(self):
        global exit_flag
        global q
        global r
        exit_flag = 1
        for t in self.threads:
            t.join()
        for e in range(q.qsize()):
            q.get().close()
        for et in range(r.qsize()):
            r.get()[1].close()


class Worker(Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        global q
        global r
        global q_lock
        global r_lock
        self.thread_id = thread_id
        self.name = name

    def run(self) -> None:
        print("starting", self.name, self.thread_id)
        try:
            self.reload()
        except:
            print("Error in thread %d. " % self.thread_id)
            print(traceback.format_exc())
        print("stopping", self.name, self.thread_id)

    def reload(self):
        global q
        global r
        global exit_flag
        while not exit_flag:
            try:
                print("ThreadID %d waiting for environment to reset." % self.thread_id)
                local_env = q.get(block=True, timeout=5)

                print(self.thread_id, "got", local_env)
                obs = local_env.reset()

                while isinstance(obs, int):
                    print("Failed to load environment, retrying... ThreadID: %d" % self.thread_id)
                    local_env = SkyRunner.CustomEnv()
                    obs = local_env.reset()

                r.put((obs, local_env))
            except queue.Empty:
                print("Queue-GET timed out. Trying again, if not exit_falg has been sat. ThreadID: %d" % self.thread_id)
                continue
