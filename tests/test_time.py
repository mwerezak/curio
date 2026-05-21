import curio
from curio.sync import Event
from curio.task import TaskCancelled, TaskTimeout
from curio.time import timeout_after, ignore_after


def test_timeout_after_expires(kernel):
    evt = Event()
    async def task():
        try:
            await evt.wait()
        except TaskCancelled:
            raise
        else:
            assert False

    async def coro():
        try:
            await timeout_after(0.25, task)
        except TaskTimeout:
            assert True
        else:
            assert False

    kernel.run(coro)


def test_timeout_after_no_timeout(kernel):
    async def task():
        try:
            await curio.sleep(0.1)
        except TaskCancelled:
            raise

    async def coro():
        try:
            await timeout_after(0.25, task)
        except TaskTimeout:
            assert False
        else:
            assert True

    kernel.run(coro)


def test_timeout_after_context_manager_expires(kernel):
    evt = Event()
    async def task():
        try:
            await evt.wait()
        except TaskCancelled:
            raise
        else:
            assert False

    async def coro():
        try:
            async with timeout_after(0.25) as s:
                await task()
        except TaskTimeout:
            assert s.expired
        else:
            assert False

    kernel.run(coro)


def test_timeout_after_context_manager_no_timeout(kernel):
    async def task():
        try:
            await curio.sleep(0.1)
        except TaskCancelled:
            raise

    async def coro():
        try:
            async with timeout_after(0.25) as s:
                await task()
        except TaskTimeout:
            assert False
        else:
            assert not s.expired

    kernel.run(coro)


def test_ignore_after_expires(kernel):
    evt = Event()
    async def task():
        try:
            await evt.wait()
        except TaskCancelled:
            raise
        else:
            return 1

    async def coro():
        assert await ignore_after(0.25, task, timeout_result=2) == 2

    kernel.run(coro)


def test_ignore_after_no_timeout(kernel):
    async def task():
        try:
            await curio.sleep(0.1)
        except TaskCancelled:
            raise
        else:
            return 1

    async def coro():
        assert await ignore_after(0.25, task, timeout_result=2) == 1

    kernel.run(coro)


def test_ignore_after_context_manager_expires(kernel):
    evt = Event()
    async def task():
        try:
            await evt.wait()
        except TaskCancelled:
            raise

    async def coro():
        async with ignore_after(0.25) as s:
            await task()
            assert False
        assert s.expired

    kernel.run(coro)


def test_ignore_after_context_manager_no_timeout(kernel):
    async def task():
        try:
            await curio.sleep(0.1)
        except TaskCancelled:
            raise
        else:
            return True

    async def coro():
        result = False
        async with ignore_after(0.25) as s:
            result = await task()
        assert result
        assert not s.expired

    kernel.run(coro)
