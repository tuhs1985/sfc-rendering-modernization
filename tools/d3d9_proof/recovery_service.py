"""One bounded owner of receiver drain/light/rebind work; never runs in SFC."""
import threading


class Service:
    def __init__(self,step):
        self.stop_event=threading.Event();self.error=None;self.steps=0
        def run():
            try:
                while not self.stop_event.is_set():
                    step();self.steps+=1
                    if self.stop_event.wait(.002):break
            except Exception as exc:self.error=exc
        self.thread=threading.Thread(target=run,name='SFC-recovery',daemon=False)
        self.thread.start()

    def check(self):
        if self.error:raise RuntimeError('Recovery service: '+str(self.error))

    def close(self):
        self.stop_event.set();self.thread.join(timeout=5)
        if self.thread.is_alive():raise RuntimeError('Recovery service did not join;do not release mapping')
