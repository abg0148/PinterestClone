import click
from flask import current_app
import psycopg2

@click.command('init-db')
def init_db_command():
    """Initialize the PostgreSQL database from schema.sql."""
    db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            with current_app.open_resource('../db/tables/init_schema.sql') as f:
                cur.execute(f.read().decode('utf-8'))
        conn.commit()
    click.echo('Database initialized.')

def init_app(app):
    app.cli.add_command(init_db_command)
