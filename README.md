# isigameko - Incident Response Training

A Flask-based incident response communication system for training teams in crisis management and professional communication under pressure.

## Features
- 💬 Team-based messaging with individual identification
- 🚨 Tutor message injection for escalating scenarios
- ⏱️ Timing analysis for debrief (tutor view only)
- 🎯 Room-based sessions with secure room codes
- 📱 Clean mobile-responsive interface
- 🔄 Manual refresh system (no continuous polling)

## Quick Start

### Local Development
```bash
pip install -r requirements.txt
python app.py
```
Visit http://localhost:8080

### Deploy to Google Cloud Run
```bash
# Production deployment
./deploy.sh
```

## Project Structure
```
isigameko/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies  
├── Dockerfile            # Container configuration
├── deploy.sh             # Deployment script
├── static/
│   └── app.css           # CSS styles (reused from polling app)
└── templates/
    ├── base.html         # Base template
    ├── intro.html        # Home page
    ├── team.html         # Team messaging interface
    └── tutor.html        # Tutor control panel
```

## Usage

### Setting Up an Exercise
1. **Create room**: Tutor visits `/ROOMCODE/tutor/TUTOR_KEY` directly - this creates the room if it doesn't exist. `TUTOR_KEY` is a shared secret set via the `TUTOR_KEY` env var (see `bin/deploy.sh`); wrong or missing key returns a plain 404
2. **Share team URL**: Give teams the URL `/ROOMCODE` directly (e.g. in a breakout room) - `/` is not a discovery page and has no room-creation form
3. **Tutor-only pages**: `/ROOMCODE/debrief/TUTOR_KEY` and `/ROOMCODE/admin/TUTOR_KEY` use the same key

### During Training
1. **Teams join**: Team members enter their name/role and start messaging
2. **Inject pressure**: Tutor sends incident updates via "Inject Incident Update"
3. **Monitor communication**: Tutor sees all messages with timing analysis
4. **Manual refresh**: Teams and tutor refresh manually to see new messages

### Message Types
- **Team messages**: Blue border, individual team member identification
- **System messages**: Red border, marked as "🚨 INCIDENT UPDATE"
- **Visual distinction**: Teams see their own messages in different color

### Debrief Analysis
- **Timing data**: Tutor sees "+Xm" relative to first message
- **Communication patterns**: Identify response delays and coordination issues
- **Copy messages**: Select and copy all messages for detailed post-exercise analysis
- **Clear messages**: Reset between scenarios

## Training Scenarios

Perfect for incident response exercises such as:
- **Fire drill simulations**: Customer dashboard failures, system outages
- **Escalation scenarios**: CEO involvement, legal compliance, media inquiries
- **Communication training**: Professional stakeholder updates under pressure
- **Team coordination**: Role-based response (Tech Lead, Communications, etc.)

## Security Features

- Room codes validated (letters, numbers, hyphens only, 2-10 chars)
- Query parameters blocked for security
- Input length limits (500 chars messages, 30 chars names)
- HTML escaping for XSS protection
- Session-based team identification

## Cost Optimization

- **No continuous polling** - eliminates expensive background requests
- **Manual refresh only** - reduces server load significantly
- **Auto-scaling to zero** - app scales down when not in use
- **Session-based storage** - no database required
- **Designed for Google Cloud free tier** (well under 2M requests/month)

## Educational Benefits

- **Authentic pressure** - simulates real incident communication challenges
- **Professional communication** - forces clear, concise updates under stress
- **Team coordination** - practices role-based crisis response
- **Timing awareness** - teaches importance of prompt communication
- **Stakeholder management** - balances technical and business communication needs

## Environment Variables

- `SECRET_KEY` - Flask session encryption key (set in production)

## Deployment Notes

- **Room lifecycle**: Rooms created when tutor first visits, cleared between exercises
- **Message persistence**: Messages stored in memory only, cleared with "Clear All Messages"
- **Concurrent access**: Handles multiple team members per room safely
- **Mobile friendly**: Works on phones/tablets for flexible team setup

---

Built for apprenticeship training programs to develop incident response and crisis communication skills.
