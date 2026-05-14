from worker.tasks import actualizar_clima


def test_task_exists():
    assert actualizar_clima.name is not None

def test_task_is_registered():
    assert actualizar_clima.name == "worker.tasks.actualizar_clima"