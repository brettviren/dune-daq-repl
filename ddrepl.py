#!/usr/bin/env python3
'''
Best is used in ipython or ptipython

>>> cmds = json.load(open("my-commands.json"))
>>> da = ddrepl.DaqApp()
>>> da(cmds[0])
>>> print (da.output())

Or give a timeout to return stdout.

>>> print(da(cmda[0], 0.1))

To kill the underlying process

>>> da.terminate()

or

>>> del(da)

'''
import os
import json
from select import select
import tempfile
import subprocess


class DaqApp:
    '''
    Start a daq_application
    '''
    def __init__(self):
        tmpdir = tempfile.mkdtemp()
        self.fname = os.path.join(tmpdir, "commands.jstream")
        os.mkfifo(self.fname)
        self.proc = subprocess.Popen(["daq_application",
                                      "--commandFacility",
                                      "file://" + self.fname],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True, bufsize=1)
        self.out = open(self.fname, "wb")

    def __del__(self):
        self.terminate()

    def terminate(self):
        'Terminate the process'
        if self.proc:
            self.proc.kill()
            self.proc = None

    def _cleanup(self):
        self.terminate()
        if self.out:
            self.out.close()
            self.out = None
        os.rmdir(os.path.dirname(self.fname))

    def output(self, timeout=0.1):
        'Get any output from the process'
        lines = list()
        while True:
            got_some = select([self.proc.stdout], [], [], timeout)[0]
            if not got_some:
                break
            lines += self.proc.stdout.readline()
        return ''.join(lines)

    def __call__(self, cmd, timeout=None):
        if self.proc is None or self.proc.poll() is not None:
            self._cleanup()
            raise RuntimeError("daq_application is gone")
        self.out.write(json.dumps(cmd).encode())
        self.out.flush()
        ret = ''
        if timeout:
            ret = self.output(timeout)
        return ret

def test_stream(cmdseq_file="fdpc-job.json"):
    '''
    Test a stream of commands.

    The input file name should be a JSON array file holding command objects.
    '''
    cmds = json.load(open(cmdseq_file))
    da = DaqApp()
    for cmd in cmds:
        print(da(cmd, 0.1))
    return da

