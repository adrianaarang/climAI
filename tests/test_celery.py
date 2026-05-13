from worker.tasks import actualizar_clima


def test_task_exists():
    assert actualizar_clima.name is not None