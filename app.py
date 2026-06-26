from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from datetime import datetime, date, timedelta
import sqlite3
import os
import io
import csv

app = Flask(__name__)
app.secret_key = 'rtp_del1_leave_tracker_2026'

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leave_tracker.db')

# Trainer data
TRAINERS = [
    {'name': 'Anoop', 'username': 'anoop', 'password': 'Anp@2741', 'doj': '2026-03-26'},
    {'name': 'Parishmita', 'username': 'parishmita', 'password': 'Prm@3852', 'doj': '2026-03-26'},
    {'name': 'Sandeep Kumar', 'username': 'sandeep', 'password': 'Sdk@4963', 'doj': '2026-03-26'},
    {'name': 'Khemchandra', 'username': 'khemchandra', 'password': 'Khm@5074', 'doj': '2026-03-26'},
    {'name': 'Neema', 'username': 'neema', 'password': 'Nma@6185', 'doj': '2026-03-26'},
    {'name': 'Ramesh Kumar', 'username': 'ramesh', 'password': 'Rmk@7296', 'doj': '2026-03-26'},
    {'name': 'Sanjay Kumar', 'username': 'sanjay', 'password': 'Sjk@8307', 'doj': '2026-03-26'},
    {'name': 'Shreya', 'username': 'shreya', 'password': 'Sry@9418', 'doj': '2026-05-17'},
    {'name': 'Kanhaiya', 'username': 'kanhaiya', 'password': 'Knh@1529', 'doj': '2026-03-26'},
    {'name': 'Manoj', 'username': 'manoj', 'password': 'Mnj@2630', 'doj': '2026-06-11'},
    {'name': 'Naveen', 'username': 'naveen', 'password': 'Nvn@3741', 'doj': '2026-05-17'},
    {'name': 'Nitish', 'username': 'nitish', 'password': 'Nts@4852', 'doj': '2026-03-26'},
    {'name': 'Rajendra', 'username': 'rajendra', 'password': 'Rjn@5963', 'doj': '2026-06-19'},
    {'name': 'Vivek', 'username': 'vivek', 'password': 'Vvk@6074', 'doj': '2026-03-26'},
    {'name': 'Yogesh Kumar', 'username': 'yogesh', 'password': 'Ygk@7185', 'doj': '2026-03-26'},
    {'name': 'Ajay Kumar', 'username': 'ajay', 'password': 'Ajk@8296', 'doj': '2026-03-26'},
]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin@rtp2026'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS trainers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        doj TEXT NOT NULL,
        location TEXT DEFAULT 'RTP-DEL1'
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trainer_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL,
        from_date TEXT NOT NULL,
        to_date TEXT NOT NULL,
        days INTEGER NOT NULL,
        reason TEXT,
        applied_on TEXT NOT NULL,
        FOREIGN KEY (trainer_id) REFERENCES trainers(id)
    )''')
    
    # Insert trainers if not exists
    for t in TRAINERS:
        existing = conn.execute('SELECT id FROM trainers WHERE username = ?', (t['username'],)).fetchone()
        if not existing:
            conn.execute('INSERT INTO trainers (name, username, password, doj) VALUES (?, ?, ?, ?)',
                        (t['name'], t['username'], t['password'], t['doj']))
    conn.commit()
    
    # Reset: Delete all leaves and re-insert only valid past leaves
    conn.execute('DELETE FROM leaves')
    conn.commit()
    
    # Pre-load past leaves (26-Apr to 25-May-2026)
    past_leaves = [
        # Khemchandra: 5 leaves (CL:1, SL:1, AL:3)
        ('khemchandra', 'CL', '2026-04-29', '2026-04-29', 1, 'Past leave'),
        ('khemchandra', 'SL', '2026-04-30', '2026-04-30', 1, 'Past leave'),
        ('khemchandra', 'AL', '2026-05-01', '2026-05-01', 1, 'Past leave'),
        ('khemchandra', 'AL', '2026-05-02', '2026-05-02', 1, 'Past leave'),
        ('khemchandra', 'AL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        # Ajay Kumar: 1 leave (CL:1)
        ('ajay', 'CL', '2026-04-28', '2026-04-28', 1, 'Past leave'),
        # Ramesh Kumar: 3 leaves (CL:1, SL:1, AL:1)
        ('ramesh', 'CL', '2026-04-27', '2026-04-27', 1, 'Past leave'),
        ('ramesh', 'SL', '2026-05-08', '2026-05-08', 1, 'Past leave'),
        ('ramesh', 'AL', '2026-05-09', '2026-05-09', 1, 'Past leave'),
        # Sanjay Kumar: 1 leave (CL:1)
        ('sanjay', 'CL', '2026-05-12', '2026-05-12', 1, 'Past leave'),
        # Sandeep Kumar: 1 leave (CL:1)
        ('sandeep', 'CL', '2026-05-07', '2026-05-07', 1, 'Past leave'),
        # Yogesh Kumar: 2 leaves (CL:1, SL:1)
        ('yogesh', 'CL', '2026-04-30', '2026-04-30', 1, 'Past leave'),
        ('yogesh', 'SL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        # Nitish: 1 leave (CL:1)
        ('nitish', 'CL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        # Vivek: 1 leave (CL:1)
        ('vivek', 'CL', '2026-05-17', '2026-05-17', 1, 'Past leave'),
        # Kanhaiya: 0 leaves in this period
        # Anoop: 5 leaves (CL:1, SL:1, AL:3)
        ('anoop', 'CL', '2026-04-28', '2026-04-28', 1, 'Past leave'),
        ('anoop', 'SL', '2026-05-08', '2026-05-08', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-09', '2026-05-09', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-10', '2026-05-10', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        # Neema: 2 leaves (CL:1, SL:1)
        ('neema', 'CL', '2026-05-09', '2026-05-09', 1, 'Past leave'),
        ('neema', 'SL', '2026-05-10', '2026-05-10', 1, 'Past leave'),
        # Shreya: 1 leave (AL:1)
        ('shreya', 'AL', '2026-05-21', '2026-05-21', 1, 'Past leave'),
    ]
        
    for username, leave_type, from_date, to_date, days, reason in past_leaves:
        trainer = conn.execute('SELECT id FROM trainers WHERE username = ?', (username,)).fetchone()
        if trainer:
            conn.execute('''INSERT INTO leaves (trainer_id, leave_type, from_date, to_date, days, reason, applied_on)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (trainer['id'], leave_type, from_date, to_date, days, reason, '2026-05-25'))
    conn.commit()
    
    conn.close()


def calculate_leave_balance(doj_str, today=None):
    """Calculate earned leaves based on DOJ"""
    if today is None:
        today = date.today()
    doj = datetime.strptime(doj_str, '%Y-%m-%d').date()
    days_worked = (today - doj).days
    if days_worked < 0:
        days_worked = 0
    
    # AL: 1 per 20 days, max 18
    al_earned = min(days_worked // 20, 18)
    # SL: 1 per 52 days, max 7
    sl_earned = min(days_worked // 52, 7)
    # CL: 1 per 52 days, max 7
    cl_earned = min(days_worked // 52, 7)
    
    return {'AL': al_earned, 'SL': sl_earned, 'CL': cl_earned}


def get_used_leaves(trainer_id):
    """Get total used leaves by type"""
    conn = get_db()
    rows = conn.execute('''SELECT leave_type, SUM(days) as total 
                          FROM leaves WHERE trainer_id = ? 
                          GROUP BY leave_type''', (trainer_id,)).fetchall()
    conn.close()
    used = {'AL': 0, 'SL': 0, 'CL': 0}
    for row in rows:
        used[row['leave_type']] = row['total']
    return used


def calculate_business_days(from_date, to_date):
    """Calculate number of days (including weekends for now)"""
    d1 = datetime.strptime(from_date, '%Y-%m-%d').date()
    d2 = datetime.strptime(to_date, '%Y-%m-%d').date()
    return (d2 - d1).days + 1


@app.route('/')
def index():
    if 'user' in session:
        if session['user'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('trainer_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password'].strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user'] = 'admin'
            session['name'] = 'Admin'
            return redirect(url_for('admin_dashboard'))
        
        conn = get_db()
        trainer = conn.execute('SELECT * FROM trainers WHERE username = ? AND password = ?',
                              (username, password)).fetchone()
        conn.close()
        
        if trainer:
            session['user'] = trainer['username']
            session['user_id'] = trainer['id']
            session['name'] = trainer['name']
            return redirect(url_for('trainer_dashboard'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def trainer_dashboard():
    if 'user' not in session or session['user'] == 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    trainer = conn.execute('SELECT * FROM trainers WHERE username = ?', (session['user'],)).fetchone()
    leaves = conn.execute('SELECT * FROM leaves WHERE trainer_id = ? ORDER BY from_date DESC', 
                         (trainer['id'],)).fetchall()
    conn.close()
    
    earned = calculate_leave_balance(trainer['doj'])
    used = get_used_leaves(trainer['id'])
    
    balance = {
        'AL': {'earned': earned['AL'], 'used': used['AL'], 'pending': earned['AL'] - used['AL']},
        'SL': {'earned': earned['SL'], 'used': used['SL'], 'pending': earned['SL'] - used['SL']},
        'CL': {'earned': earned['CL'], 'used': used['CL'], 'pending': earned['CL'] - used['CL']},
    }
    
    return render_template('trainer_dashboard.html', trainer=trainer, balance=balance, leaves=leaves)


@app.route('/apply-leave', methods=['GET', 'POST'])
def apply_leave():
    if 'user' not in session or session['user'] == 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    trainer = conn.execute('SELECT * FROM trainers WHERE username = ?', (session['user'],)).fetchone()
    
    if request.method == 'POST':
        leave_type = request.form['leave_type']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        reason = request.form.get('reason', '')
        
        days = calculate_business_days(from_date, to_date)
        
        # Block leaves before 26-May-2026
        min_date = '2026-05-26'
        if from_date < min_date:
            flash('Cannot apply leave before 26-May-2026. Contact admin for past leaves.', 'error')
        elif days <= 0:
            flash('Invalid date range', 'error')
        else:
            # Check balance
            earned = calculate_leave_balance(trainer['doj'])
            used = get_used_leaves(trainer['id'])
            available = earned[leave_type] - used[leave_type]
            
            if days > available:
                flash(f'Insufficient {leave_type} balance. Available: {available}, Requested: {days}', 'error')
            else:
                conn.execute('''INSERT INTO leaves (trainer_id, leave_type, from_date, to_date, days, reason, applied_on)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (trainer['id'], leave_type, from_date, to_date, days, reason, 
                             date.today().strftime('%Y-%m-%d')))
                conn.commit()
                flash(f'{leave_type} for {days} day(s) applied successfully!', 'success')
                conn.close()
                return redirect(url_for('trainer_dashboard'))
    
    earned = calculate_leave_balance(trainer['doj'])
    used = get_used_leaves(trainer['id'])
    balance = {
        'AL': earned['AL'] - used['AL'],
        'SL': earned['SL'] - used['SL'],
        'CL': earned['CL'] - used['CL'],
    }
    
    conn.close()
    return render_template('apply_leave.html', balance=balance)


@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    trainers = conn.execute('SELECT * FROM trainers ORDER BY name').fetchall()
    
    trainer_data = []
    for t in trainers:
        earned = calculate_leave_balance(t['doj'])
        used = get_used_leaves(t['id'])
        trainer_data.append({
            'id': t['id'],
            'name': t['name'],
            'doj': t['doj'],
            'al_earned': earned['AL'], 'al_used': used['AL'], 'al_pending': earned['AL'] - used['AL'],
            'sl_earned': earned['SL'], 'sl_used': used['SL'], 'sl_pending': earned['SL'] - used['SL'],
            'cl_earned': earned['CL'], 'cl_used': used['CL'], 'cl_pending': earned['CL'] - used['CL'],
        })
    
    conn.close()
    return render_template('admin_dashboard.html', trainers=trainer_data)


@app.route('/admin/leaves')
def admin_leaves():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    leaves = conn.execute('''SELECT l.*, t.name as trainer_name 
                            FROM leaves l JOIN trainers t ON l.trainer_id = t.id 
                            ORDER BY l.from_date DESC''').fetchall()
    conn.close()
    return render_template('admin_leaves.html', leaves=leaves)


@app.route('/admin/download')
def admin_download():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    trainers = conn.execute('SELECT * FROM trainers ORDER BY name').fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'DOJ', 'AL Earned', 'AL Used', 'AL Pending', 
                     'SL Earned', 'SL Used', 'SL Pending',
                     'CL Earned', 'CL Used', 'CL Pending'])
    
    for t in trainers:
        earned = calculate_leave_balance(t['doj'])
        used = get_used_leaves(t['id'])
        writer.writerow([
            t['name'], t['doj'],
            earned['AL'], used['AL'], earned['AL'] - used['AL'],
            earned['SL'], used['SL'], earned['SL'] - used['SL'],
            earned['CL'], used['CL'], earned['CL'] - used['CL'],
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'Leave_Report_{date.today().strftime("%d%m%Y")}.csv'
    )


@app.route('/admin/download-detail')
def admin_download_detail():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db()
    leaves = conn.execute('''SELECT l.*, t.name as trainer_name 
                            FROM leaves l JOIN trainers t ON l.trainer_id = t.id 
                            ORDER BY t.name, l.from_date''').fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Trainer Name', 'Leave Type', 'From Date', 'To Date', 'Days', 'Reason', 'Applied On'])
    
    for l in leaves:
        writer.writerow([l['trainer_name'], l['leave_type'], l['from_date'], 
                        l['to_date'], l['days'], l['reason'], l['applied_on']])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'Leave_Detail_Report_{date.today().strftime("%d%m%Y")}.csv'
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
