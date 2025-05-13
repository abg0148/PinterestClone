import click
from flask import current_app
import psycopg2
from flask.cli import with_appcontext
from app.routes.auth import create_default_boards_for_existing_users

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

def init_cli(app):
    @app.cli.command('create-default-boards')
    @with_appcontext
    def create_default_boards():
        """Create default 'Unorganized Ideas' boards for all existing users."""
        click.echo('Creating default boards for existing users...')
        create_default_boards_for_existing_users()
        click.echo('Done!')
