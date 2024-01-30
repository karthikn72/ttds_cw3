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
2. Install required python packages and start virtual env with pipenv
```
pip install pipenv
pipenv install -r requirements.txt
pipenv shell
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
### API Endpoints
- `POST /events`: Create a new event. The request body should be a JSON object with a `description` field. Returns the created event.

- `GET /events`: Get all events. Returns a list of all events.

- `GET /events/<id>`: Get a single event by its ID. Replace `<id>` with the ID of the event you want to get. Returns the requested event.

- `DELETE /events/<id>`: Delete a single event by its ID. Replace `<id>` with the ID of the event you want to delete. Returns a confirmation message.

- `PUT /events/<id>`: Update a single event by its ID. Replace `<id>` with the ID of the event you want to update. The request body should be a JSON object with a `description` field. Returns the updated event.

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


