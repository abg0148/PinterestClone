# install requirements
```bash
pip install -r requirements.txt
```

# create postgres database
```bash
createdb pinterest_clone_dev
```

# create a .env file like so in the home directory
```bash
FLASK_ENV=development
SECRET_KEY=c6c6917cdb05944b7e90beff1c8b0138
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
