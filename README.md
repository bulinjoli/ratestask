# Rates task for xeneta

Set up is not complicated, only run your docker file for creating db

```bash
docker build -t ratestask .
```

```bash
docker run -p 0.0.0.0:5432:5432 --name ratestask ratestask
```

```bash
PGPASSWORD=ratestask psql -h 127.0.0.1 -U postgres
```

And then create virtual env with commands

``` shell
virtualenv ratestask
source ratestask/bin/activate
```
Install requirements.txt, I am using pip3 for python3

``` shell
pip3 install -r requirements.txt
```

Create env variable for flask and run flask for swagger

``` shell
cd ratestask
export APP_NAME=app.py
flask run
```

Postgress connection string should be the same for your environment but in case its not you will have to change it