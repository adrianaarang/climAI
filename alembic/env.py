import sys
from logging.config import fileConfig
from os.path import abspath, dirname

from sqlalchemy import engine_from_config, pool
from alembic import context

# Agregar la raíz del proyecto al sys.path
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Importar configuraciones y modelos
from app.core.config import settings
from app.db.base import Base

# Configurar Alembic
config = context.config

# Configurar logs (alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Definir metadata de los modelos para el autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Ejecuta las migraciones en modo 'offline'.
    
    Configura el contexto con solo una URL y no un Engine.
    """
    # Transformar la URL asíncrona a síncrona para Alembic
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta las migraciones en modo 'online'.
    
    Crea un Engine y asocia una conexión al contexto.
    """
    # Obtener la sección principal del .ini
    configuration = config.get_section(config.config_ini_section)
    
    # Sobrescribir la URL del .ini con la de Settings (asíncrona a síncrona)
    sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    configuration["sqlalchemy.url"] = sync_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Determinar si ejecutar en modo offline u online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()