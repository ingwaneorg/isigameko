from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import uuid
import re
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-for-development')

# Limit the number of rooms and messages
MAX_ROOMS = 10
MAX_MESSAGES_PER_ROOM = 100

# In-memory storage
rooms = {}

def validate_room_code(room_code):
    """Validate room code: only letters, numbers, hyphens, 2-10 characters"""
    return bool(re.match(r'^[A-Za-z0-9-]{2,10}$', room_code))

def get_team_id():
    """Get or create team ID for this session"""
    if 'team_id' not in session:
        team_uuid = str(uuid.uuid4())
        session['team_id'] = team_uuid
    return session['team_id']

@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/join', methods=['POST'])
def join_room():
    room_code = request.form.get('room_code', '').upper().strip()
    role = request.form.get('role')  # 'team' or 'tutor'
    
    if not room_code or not validate_room_code(room_code):
        return redirect(url_for('intro'))
    
    if role == 'tutor':
        return redirect(url_for('tutor_page', room_code=room_code))
    else:
        return redirect(url_for('team_page', room_code=room_code))

@app.route('/<room_code>')
def team_page(room_code):
    # Block any query parameters for security
    if request.args:
        return "Forbidden", 403
    
    if not validate_room_code(room_code):
        return "Invalid room code", 400
        
    room_code = room_code.upper()
    
    # Show 404 error if tutor hasn't created the room
    if room_code not in rooms:
        return "Room not found", 404

    team_id = get_team_id()
    
    # Get team name if they've set one
    team_name = session.get('team_name', '')
    
    return render_template('team.html', 
                         room=rooms[room_code], 
                         team_id=team_id,
                         team_name=team_name)

@app.route('/<room_code>/tutor')
def tutor_page(room_code):
    # Block any query parameters for security
    if request.args:
        return "Forbidden", 403
    
    if not validate_room_code(room_code):
        return "Invalid room code", 400
        
    room_code = room_code.upper()
    
    # Initialise room if it doesn't exist
    if room_code not in rooms:
        # Limit number of rooms
        if len(rooms) >= MAX_ROOMS:
            return "Maximum number of rooms reached", 403

        rooms[room_code] = {
            'code': room_code,
            'description': f'Incident Response Room {room_code}',
            'messages': [],
            'createdDate': datetime.now().isoformat()
        }
    
    return render_template('tutor.html', 
                         room=rooms[room_code])

# Save the database if in DEBUG mode
def save_db_json():
    if app.debug:
        with open('db.json', 'w') as f:
            json.dump(rooms, f, indent=2, default=str)

@app.route('/<room_code>/send-message', methods=['POST'])
def send_message(room_code):
    room_code = room_code.upper()
    team_id = get_team_id()
    
    if not validate_room_code(room_code):
        return jsonify({'success': False, 'error': 'Invalid room code'})
    
    if room_code not in rooms:
        return jsonify({'success': False, 'error': 'Room not found'})
    
    data = request.get_json()
    message_text = data.get('message', '').strip()
    team_name = data.get('team_name', '').strip()
    
    # Validate inputs
    if not message_text:
        return jsonify({'success': False, 'error': 'Message cannot be empty'})
    
    if len(message_text) > 500:  # Limit message length
        return jsonify({'success': False, 'error': 'Message too long (max 500 characters)'})
    
    if len(team_name) > 30:  # Limit team name length
        return jsonify({'success': False, 'error': 'Team name too long (max 30 characters)'})
    
    # Check message limit
    if len(rooms[room_code]['messages']) >= MAX_MESSAGES_PER_ROOM:
        return jsonify({'success': False, 'error': 'Room message limit reached'})
    
    # Store team name in session
    if team_name:
        session['team_name'] = team_name
    
    # Create message
    message = {
        'id': str(uuid.uuid4()),
        'team_id': team_id,
        'team_name': team_name or 'Anonymous Team',
        'message': message_text,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to room
    rooms[room_code]['messages'].append(message)
    
    save_db_json()
    return jsonify({'success': True, 'message': message})

@app.route('/<room_code>/get-messages')
def get_messages(room_code):
    room_code = room_code.upper()
    
    if not validate_room_code(room_code):
        return jsonify({'success': False, 'error': 'Invalid room code'})
    
    if room_code not in rooms:
        return jsonify({'success': False, 'error': 'Room not found'})
    
    return jsonify({
        'success': True, 
        'messages': rooms[room_code]['messages']
    })

@app.route('/<room_code>/clear-messages', methods=['POST'])
def clear_messages(room_code):
    room_code = room_code.upper()
    
    if not validate_room_code(room_code):
        return jsonify({'success': False, 'error': 'Invalid room code'})
    
    if room_code not in rooms:
        return jsonify({'success': False, 'error': 'Room not found'})
    
    # Clear all messages
    rooms[room_code]['messages'] = []
    
    save_db_json()
    return jsonify({'success': True})

@app.route('/<room_code>/inject-message', methods=['POST'])
def inject_message(room_code):
    """Tutor can inject pressure messages during the exercise"""
    room_code = room_code.upper()
    
    if not validate_room_code(room_code):
        return jsonify({'success': False, 'error': 'Invalid room code'})
    
    if room_code not in rooms:
        return jsonify({'success': False, 'error': 'Room not found'})
    
    data = request.get_json()
    message_text = data.get('message', '').strip()
    
    if not message_text:
        return jsonify({'success': False, 'error': 'Message cannot be empty'})
    
    if len(message_text) > 500:
        return jsonify({'success': False, 'error': 'Message too long (max 500 characters)'})
    
    # Create system message
    message = {
        'id': str(uuid.uuid4()),
        'team_id': 'SYSTEM',
        'team_name': '🚨 INCIDENT UPDATE',
        'message': message_text,
        'timestamp': datetime.now().isoformat()
    }
    
    rooms[room_code]['messages'].append(message)
    
    save_db_json()
    return jsonify({'success': True, 'message': message})

@app.route("/api")
def block_api_root():
    return "Access to /api is not allowed", 403

@app.route("/api/rooms")
def api_rooms():
    room_summaries = []

    for room_code, room in rooms.items():
        room_summaries.append({
            'code': room_code,
            'description': room.get('description', ''),
            'message_count': len(room.get('messages', [])),
            'created_date': room.get('createdDate'),
        })

    return jsonify(room_summaries)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
