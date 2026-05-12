from worker.tasks import actualizar_clima

result = actualizar_clima.delay(
    40.4168,
    -3.7038
)

print(result.id)