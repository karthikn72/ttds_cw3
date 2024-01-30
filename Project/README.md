# TTDS Project Template

Simple overview of use/purpose.

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies
```
pipenv install flask flask-sqlalchemy psycopg2 python-dotenv flask-cors
```

### Running Backend
1. Navigate to backend
```
cd backend
```
2. Install required python packages
```
pip install -r requirements.txt
```
3. Set up the database if it isnt already set up:
```
python
>>> from app import db
>>> db.create_all()
>>> exit()
```
4. Run
```
flask run
```


### Running Frontend
1. switch directory
```
cd frontend
```
2. Install dependencies
```
npm install axios date-fns
```
3. start
```
npm start
```


