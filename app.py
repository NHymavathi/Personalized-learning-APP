
#!/usr/bin/env python
"""
Personalized Learning Assistant - Flask Application
A web application that generates personalized learning materials based on user profiles.
"""
import os
import sqlite3
import hashlib
import json
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, 
    session, jsonify, flash, url_for
)

# Import content generators
from content_generator import generate_learning_content
from llm import generate_learning_material

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
DATABASE = 'users.db'

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            learning_style TEXT DEFAULT 'Reading',
            level TEXT DEFAULT 'Beginner',
            accuracy INTEGER DEFAULT 80,
            interests TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Learning history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Add created_at column if it doesn't exist (for existing databases)
    try:
        cursor.execute('SELECT created_at FROM user_profiles LIMIT 1')
    except sqlite3.OperationalError:
        # SQLite doesn't allow non-constant default, so we add the column first
        try:
            cursor.execute('ALTER TABLE user_profiles ADD COLUMN created_at TIMESTAMP')
            # Update existing rows - use a simple string value for compatibility
            cursor.execute("UPDATE user_profiles SET created_at = datetime('now') WHERE created_at IS NULL")
        except:
            pass  # Column might already exist or other issue
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def get_user_by_username(username):
    """Get user by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_or_create_profile(user_id):
    """Get or create user profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    profile = cursor.fetchone()
    
    if not profile:
        cursor.execute(
            'INSERT INTO user_profiles (user_id) VALUES (?)',
            (user_id,)
        )
        conn.commit()
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        profile = cursor.fetchone()
    
    conn.close()
    return profile


def save_learning_history(user_id, topic, content):
    """Save learning content to history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO learning_history (user_id, topic, content) VALUES (?, ?, ?)',
        (user_id, topic, content)
    )
    conn.commit()
    conn.close()


# ============================================================================
# AUTHENTICATION DECORATORS
# ============================================================================

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Homepage - shows the learning form."""
    user_id = session.get('user_id')
    profile = None
    
    if user_id:
        profile = get_or_create_profile(user_id)
    
    return render_template('index.html', profile=profile, user=session.get('username'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('signup.html')
        
        # Check if username exists
        if get_user_by_username(username):
            flash('Username already exists. Please choose another.', 'error')
            return render_template('signup.html')
        
        # Create user
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, hash_password(password))
            )
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f'Error creating account: {e}', 'error')
        finally:
            conn.close()
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter username and password.', 'error')
            return render_template('login.html')
        
        user = get_user_by_username(username)
        
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout."""
    username = session.get('username', 'User')
    session.clear()
    flash(f'You have been logged out. Goodbye, {username}!', 'success')
    return redirect(url_for('login'))


@app.route('/learn', methods=['POST'])
@login_required
def learn():
    """Generate personalized learning content."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        topic = data.get('topic', '').strip()
        user_id = session.get('user_id')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Please provide a topic'}), 400
        
        # Get user profile
        profile = get_or_create_profile(user_id)
        
        # Extract profile settings
        learning_style = profile['learning_style'] if profile else 'Reading'
        level = profile['level'] if profile else 'Beginner'
        accuracy = profile['accuracy'] if profile else 80
        interests = profile['interests'] if profile else ''
        # Generate content using local generator (llm.py returns simple string)
        try:
            profile_dict = {
                'learning_style': learning_style,
                'level': level,
                'accuracy': accuracy,
                'interests': interests
            }
            llm_content = generate_learning_material(topic, profile_dict)
            
            # Create topic URL-friendly string
            topic_url = topic.lower().replace(' ', '-').replace('programming', '').strip('-')
            
            # Convert to dictionary format with diverse resources
            content = {
                "topic": topic,
                "level": level,
                "explanation": llm_content,
                "key_topics": [
                    f"Introduction to {topic}",
                    f"Core concepts of {topic}",
                    f"Advanced concepts in {topic}",
                ],
                "practice_tasks": [
                    f"Practice {topic} through exercises",
                    f"Build a project using {topic}",
                ],
                "next_steps": [
                    f"Explore advanced {topic} topics",
                    f"Apply {topic} in real projects",
                ],
                "resources": [
                    {"title": f"{topic} Tutorial - W3Schools", "website": "W3Schools", "url": f"https://www.w3schools.com/{topic.lower().replace(' ', '')}/", "type": "Documentation", "icon": "📚"},
                    {"title": f"{topic} Tutorial - GeeksforGeeks", "website": "GeeksforGeeks", "url": f"https://www.geeksforgeeks.org/{topic.lower().replace(' ', '-')}/", "type": "Tutorial", "icon": "💻"},
                    {"title": f"Learn {topic} - YouTube", "website": "YouTube", "url": f"https://www.youtube.com/results?search_query=learn+{topic.lower().replace(' ', '+')}+tutorial", "type": "Video", "icon": "🎥"},
                    {"title": f"{topic} Documentation - MDN", "website": "MDN Web Docs", "url": f"https://developer.mozilla.org/en-US/search?q={topic.lower().replace(' ', '+')}", "type": "Documentation", "icon": "🌐"},
                    {"title": f"{topic} on Coursera", "website": "Coursera", "url": f"https://www.coursera.org/search?query={topic.lower().replace(' ', '%20')}", "type": "Course", "icon": "🎓"},
                    {"title": f"{topic} on Udemy", "website": "Udemy", "url": f"https://www.udemy.com/search/?q={topic.lower().replace(' ', '%20')}", "type": "Course", "icon": "📖"},
                    {"title": f"{topic} - Wikipedia", "website": "Wikipedia", "url": f"https://en.wikipedia.org/wiki/{topic.lower().replace(' ', '_')}", "type": "Reference", "icon": "📝"},
                    {"title": f"{topic} on Stack Overflow", "website": "Stack Overflow", "url": f"https://stackoverflow.com/questions/tagged/{topic.lower().replace(' ', '-')}", "type": "Q&A", "icon": "❓"},
                    {"title": f"{topic} Practice - HackerRank", "website": "HackerRank", "url": f"https://www.hackerrank.com/domains/tutorials/10-days-of-{topic.lower().replace(' ', '-')}", "type": "Practice", "icon": "⚡"},
                    {"title": f"ChatGPT - Ask about {topic}", "website": "ChatGPT", "url": "https://chat.openai.com/", "type": "AI Assistant", "icon": "🤖"},
                ]
            }
        except Exception as e:
            # Fallback to local content generator
            content = generate_learning_content(
                topic=topic,
                level=level,
                learning_style=learning_style,
                interests=interests,
                accuracy=accuracy
            )
        
        # Save to history
        save_learning_history(user_id, topic, json.dumps(content))
        
        return jsonify({
            'success': True,
            'content': content
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating content: {str(e)}'
        }), 500


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile settings."""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        learning_style = request.form.get('learning_style', 'Reading')
        level = request.form.get('level', 'Beginner')
        accuracy = int(request.form.get('accuracy', 80))
        interests = request.form.get('interests', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_profiles 
            SET learning_style = ?, level = ?, accuracy = ?, interests = ?, 
            updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (learning_style, level, accuracy, interests, user_id))
        conn.commit()
        conn.close()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('index'))
    
    profile = get_or_create_profile(user_id)
    return render_template('profile.html', profile=profile)


@app.route('/history')
@login_required
def history():
    """View learning history."""
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT topic, content, created_at 
        FROM learning_history 
        WHERE user_id = ? 
        ORDER BY created_at DESC
        LIMIT 20
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    # Parse JSON content for each history item
    history = []
    for row in rows:
        try:
            content = json.loads(row['content'])
        except (json.JSONDecodeError, TypeError):
            content = {}
        history.append({
            'topic': row['topic'],
            'content': content,
            'created_at': row['created_at']
        })
    
    return render_template('history.html', history=history)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('error.html', error_code=500, message='Server error'), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(debug=True)

