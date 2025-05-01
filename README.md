# install requirements
```bash
pip install -r requirements.txt
```

# create postgres database
```bash
createdb pinterest_clone_dev
```

# generate a secret key like so in python
```python
import secrets
secrets.token_hex(16)
```

# create a .env file like so in the home directory
```bash
FLASK_ENV=development
SECRET_KEY=<generated-secret-key>
DATABASE_URL=postgresql://<username>:<password>@localhost/pinterest_clone_dev
```

# first run this
```bash
flask init-db
```
# then run this
```
flask run
```
