from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/app-database'
db = SQLAlchemy(app)
CORS(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Event: {self.description}"
    
    def __init__(self, description):
        self.description = description

def format_event(event):
    return {
        'id': event.id,
        'description': event.description,
        'created_at': event.created_at
    }

#create an event
@app.route('/events', methods=['POST'])
def create_event():
    description = request.json['description'] # Get description from request body
    event = Event(description)                # Create new event
    db.session.add(event)                     # Add to database
    db.session.commit()                       # Save
    return format_event(event)                # Return formatted event as JSON so frontend can use it for something

#get all events
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.order_by(Event.id.asc()).all()
    event_list = []
    for event in events:
        event_list.append(format_event(event))
    return {'events': event_list}

#get single event
@app.route('/events/<id>', methods=['GET'])
def get_event(id):
    event = Event.query.filter_by(id=id).one() #.first() gives the first result. .one() errors out if more than one but since using unique id, it's the same
    formatted_event = format_event(event)
    return {'event': formatted_event}

#delete an event
@app.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.filter_by(id=id).one()
    db.session.delete(event)
    db.session.commit()
    return f'Event with id {id} has been deleted'

#update an event
@app.route('/events/<id>', methods=['PUT'])
def update_event(id):
    event = Event.query.filter_by(id=id)
    description = request.json['description']
    event.update(dict(description=description, created_at=datetime.utcnow()))
    db.session.commit()
    return {'event': format_event(event.one())}

if __name__ == '__main__':
    app.run()