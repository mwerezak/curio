"""
Copyright (C) Natural Resources Canada - All Rights Reserved.

Unauthorized copying of this file, via any medium is strictly prohibited.
Proprietary and confidential.

| Author: Mike Werezak <mike.werezak@nrcan-rncan.gc.ca>
| Created: 2026-03-01
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from curio import *
from curio.sched import SchedFIFO

if TYPE_CHECKING:
    pass


class TestSchedFIFO:
    def test_suspend_then_wake(self, kernel):
        results = []
        async def worker(sched):
            results.append('suspend')
            await sched.suspend()
            results.append('worker_done')

        async def waker(seconds):
            sched = SchedFIFO()
            await spawn(worker, sched)
            results.append('sleep')
            await sleep(seconds)
            results.append('wake')
            await sched.wake(1)
            results.append('waker_done')

        kernel.run(waker(1))
        kernel.run()  # allow the worker to finish

        assert results == [
            'sleep',
            'suspend',
            'wake',
            'waker_done',
            'worker_done',
        ]

    def test_wait_when_queue_empty(self, kernel):
        async def main():
            sched = SchedFIFO()
            await sched.wake(1)

        kernel.run(main)
