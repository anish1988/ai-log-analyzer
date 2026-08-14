import asyncio

from app.ai.progress.publisher import ProgressPublisher
from app.ai.progress.events import ProgressStatus


async def main():

    publisher = ProgressPublisher()

    queue_a = await publisher.subscribe(
        'TEST-A'
    )

    queue_b = await publisher.subscribe(
        'TEST-B'
    )

    await publisher.publish(
        request_id='TEST-A',
        task_id='test_task',
        task_name='Test Task',
        status=ProgressStatus.RUNNING,
        progress=50,
        message='Testing request A',
    )

    event_a = await queue_a.get()

    print('=' * 100)
    print('PUBLISHER SUBSCRIBER TEST')
    print('=' * 100)

    print('Queue A received :', event_a.request_id)
    print('Queue B empty    :', queue_b.empty())

    assert event_a.request_id == 'TEST-A'
    assert queue_b.empty()

    await publisher.unsubscribe(
        'TEST-A',
        queue_a,
    )

    await publisher.unsubscribe(
        'TEST-B',
        queue_b,
    )

    print('TEST RESULT      : PASS')
    print('=' * 100)


asyncio.run(main())
