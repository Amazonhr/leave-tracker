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
    
    # Only pre-load past leaves if table is empty (first deploy)
    existing_leaves = conn.execute('SELECT COUNT(*) as cnt FROM leaves').fetchone()
    if existing_leaves['cnt'] == 0:
        # Pre-load all leaves from local database
        past_leaves = [
        ('ajay', 'CL', '2026-04-28', '2026-04-28', 1, 'Past leave'),
        ('ajay', 'SL', '2026-06-13', '2026-06-13', 1, ''),
        ('ajay', 'AL', '2026-06-16', '2026-06-16', 1, ''),
        ('ajay', 'AL', '2026-06-24', '2026-06-25', 2, ''),
        ('anoop', 'CL', '2026-04-28', '2026-04-28', 1, 'Past leave'),
        ('anoop', 'SL', '2026-05-08', '2026-05-08', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-09', '2026-05-09', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-10', '2026-05-10', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        ('anoop', 'AL', '2026-05-27', '2026-05-27', 1, ''),
        ('kanhaiya', 'CL', '2026-06-17', '2026-06-17', 1, ''),
        ('khemchandra', 'CL', '2026-05-01', '2026-05-01', 1, ''),
        ('neema', 'SL', '2026-06-09', '2026-06-09', 1, ''),
        ('neema', 'CL', '2026-06-18', '2026-06-18', 1, ''),
        ('nitish', 'CL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        ('nitish', 'SL', '2026-05-28', '2026-05-28', 1, ''),
        ('parishmita', 'AL', '2026-06-02', '2026-06-05', 4, ''),
        ('parishmita', 'SL', '2026-06-06', '2026-06-06', 1, ''),
        ('parishmita', 'CL', '2026-06-09', '2026-06-09', 1, ''),
        ('ramesh', 'CL', '2026-04-27', '2026-04-27', 1, 'Past leave'),
        ('ramesh', 'SL', '2026-05-08', '2026-05-08', 1, 'Past leave'),
        ('sandeep', 'CL', '2026-05-07', '2026-05-07', 1, 'Past leave'),
        ('sanjay', 'CL', '2026-05-12', '2026-05-12', 1, 'Past leave'),
        ('shreya', 'AL', '2026-05-21', '2026-05-21', 1, 'Past leave'),
        ('shreya', 'AL', '2026-06-09', '2026-06-09', 1, ''),
        ('vivek', 'CL', '2026-05-17', '2026-05-17', 1, 'Past leave'),
        ('vivek', 'SL', '2026-06-13', '2026-06-13', 1, ''),
        ('vivek', 'AL', '2026-06-25', '2026-06-25', 1, ''),
        ('yogesh', 'CL', '2026-04-30', '2026-04-30', 1, 'Past leave'),
        ('yogesh', 'SL', '2026-05-18', '2026-05-18', 1, 'Past leave'),
        ('yogesh', 'AL', '2026-06-13', '2026-06-13', 1, ''),
        ('yogesh', 'AL', '2026-06-22', '2026-06-22', 1, ''),
        ('yogesh', 'AL', '2026-06-25', '2026-06-25', 1, ''),
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
        
        # Block leaves outside allowed payroll window
        today = date.today()
        
        # Grace period: Until 30-Jun-2026, allow 26-May to 25-Jun
        grace_end = date(2026, 6, 30)
        if today <= grace_end:
            payroll_start = date(2026, 5, 26)
            payroll_end = date(2026, 6, 25)
        else:
            # Normal payroll month logic (26th to 25th)
            if today.day >= 26:
                payroll_start = date(today.year, today.month, 26)
                if today.month == 12:
                    payroll_end = date(today.year + 1, 1, 25)
                else:
                    payroll_end = date(today.year, today.month + 1, 25)
            else:
                if today.month == 1:
                    payroll_start = date(today.year - 1, 12, 26)
                else:
                    payroll_start = date(today.year, today.month - 1, 26)
                payroll_end = date(today.year, today.month, 25)
        
        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        
        if from_date_obj < payroll_start or from_date_obj > payroll_end:
            flash(f'You can only apply leave between {payroll_start.strftime("%d-%b-%Y")} and {payroll_end.strftime("%d-%b-%Y")}.', 'error')
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


# --- ADMIN: Reset Password ---
@app.route('/admin/reset-password/<int:trainer_id>', methods=['GET', 'POST'])
def admin_reset_password(trainer_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    trainer = conn.execute('SELECT * FROM trainers WHERE id = ?', (trainer_id,)).fetchone()
    if request.method == 'POST':
        new_password = request.form['new_password'].strip()
        if len(new_password) < 4:
            flash('Password must be at least 4 characters', 'error')
        else:
            conn.execute('UPDATE trainers SET password = ? WHERE id = ?', (new_password, trainer_id))
            conn.commit()
            flash(f'Password updated for {trainer["name"]}', 'success')
            conn.close()
            return redirect(url_for('admin_dashboard'))
    conn.close()
    return render_template('admin_reset_password.html', trainer=trainer)


# --- ADMIN: Add Trainer ---
@app.route('/admin/add-trainer', methods=['GET', 'POST'])
def admin_add_trainer():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name'].strip()
        username = request.form['username'].strip().lower()
        password = request.form['password'].strip()
        doj = request.form['doj']
        conn = get_db()
        existing = conn.execute('SELECT id FROM trainers WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists', 'error')
        else:
            conn.execute('INSERT INTO trainers (name, username, password, doj) VALUES (?, ?, ?, ?)',
                        (name, username, password, doj))
            conn.commit()
            flash(f'Trainer {name} added successfully!', 'success')
            conn.close()
            return redirect(url_for('admin_dashboard'))
        conn.close()
    return render_template('admin_add_trainer.html')


# --- ADMIN: Remove Trainer ---
@app.route('/admin/remove-trainer/<int:trainer_id>', methods=['POST'])
def admin_remove_trainer(trainer_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    trainer = conn.execute('SELECT name FROM trainers WHERE id = ?', (trainer_id,)).fetchone()
    conn.execute('DELETE FROM leaves WHERE trainer_id = ?', (trainer_id,))
    conn.execute('DELETE FROM trainers WHERE id = ?', (trainer_id,))
    conn.commit()
    conn.close()
    flash(f'Trainer {trainer["name"]} removed', 'success')
    return redirect(url_for('admin_dashboard'))


# --- ADMIN: Delete a Leave ---
@app.route('/admin/delete-leave/<int:leave_id>', methods=['POST'])
def admin_delete_leave(leave_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM leaves WHERE id = ?', (leave_id,))
    conn.commit()
    conn.close()
    flash('Leave record deleted', 'success')
    return redirect(request.referrer or url_for('admin_leaves'))


# --- ADMIN: Individual Trainer View ---
@app.route('/admin/trainer/<int:trainer_id>')
def admin_trainer_view(trainer_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    trainer = conn.execute('SELECT * FROM trainers WHERE id = ?', (trainer_id,)).fetchone()
    leaves = conn.execute('SELECT * FROM leaves WHERE trainer_id = ? ORDER BY from_date DESC',
                         (trainer_id,)).fetchall()
    conn.close()
    earned = calculate_leave_balance(trainer['doj'])
    used = get_used_leaves(trainer_id)
    balance = {
        'AL': {'earned': earned['AL'], 'used': used['AL'], 'pending': earned['AL'] - used['AL']},
        'SL': {'earned': earned['SL'], 'used': used['SL'], 'pending': earned['SL'] - used['SL']},
        'CL': {'earned': earned['CL'], 'used': used['CL'], 'pending': earned['CL'] - used['CL']},
    }
    return render_template('admin_trainer_view.html', trainer=trainer, balance=balance, leaves=leaves)


# --- ADMIN: Apply Leave on Behalf ---
@app.route('/admin/apply-leave', methods=['GET', 'POST'])
def admin_apply_leave():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    trainers = conn.execute('SELECT * FROM trainers ORDER BY name').fetchall()
    if request.method == 'POST':
        trainer_id = int(request.form['trainer_id'])
        leave_type = request.form['leave_type']
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        reason = request.form.get('reason', 'Applied by Admin')
        days = calculate_business_days(from_date, to_date)
        if days <= 0:
            flash('Invalid date range', 'error')
        else:
            conn.execute('''INSERT INTO leaves (trainer_id, leave_type, from_date, to_date, days, reason, applied_on)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (trainer_id, leave_type, from_date, to_date, days, reason,
                         date.today().strftime('%Y-%m-%d')))
            conn.commit()
            flash(f'Leave applied successfully for {days} day(s)!', 'success')
            conn.close()
            return redirect(url_for('admin_dashboard'))
    conn.close()
    return render_template('admin_apply_leave.html', trainers=trainers)


# --- ADMIN: Monthly Payroll Download ---
@app.route('/admin/download-monthly')
def admin_download_monthly():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    today = date.today()
    if today.day >= 26:
        payroll_start = date(today.year, today.month, 26)
        if today.month == 12:
            payroll_end = date(today.year + 1, 1, 25)
        else:
            payroll_end = date(today.year, today.month + 1, 25)
    else:
        if today.month == 1:
            payroll_start = date(today.year - 1, 12, 26)
        else:
            payroll_start = date(today.year, today.month - 1, 26)
        payroll_end = date(today.year, today.month, 25)
    conn = get_db()
    trainers = conn.execute('SELECT * FROM trainers ORDER BY name').fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'DOJ', 'AL Used (This Month)', 'SL Used (This Month)',
                     'CL Used (This Month)', 'Total Days on Leave'])
    for t in trainers:
        leaves = conn.execute('''SELECT leave_type, SUM(days) as total FROM leaves
                               WHERE trainer_id = ? AND from_date >= ? AND from_date <= ?
                               GROUP BY leave_type''',
                             (t['id'], payroll_start.strftime('%Y-%m-%d'),
                              payroll_end.strftime('%Y-%m-%d'))).fetchall()
        monthly = {'AL': 0, 'SL': 0, 'CL': 0}
        for l in leaves:
            monthly[l['leave_type']] = l['total']
        total = monthly['AL'] + monthly['SL'] + monthly['CL']
        writer.writerow([t['name'], t['doj'], monthly['AL'], monthly['SL'], monthly['CL'], total])
    conn.close()
    output.seek(0)
    month_label = payroll_start.strftime('%d%b') + '_to_' + payroll_end.strftime('%d%b%Y')
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'Payroll_Leave_{month_label}.csv'
    )


# --- ADMIN: Download by Custom Date Range ---
@app.route('/admin/download-range', methods=['GET', 'POST'])
def admin_download_range():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        conn = get_db()
        trainers = conn.execute('SELECT * FROM trainers ORDER BY name').fetchall()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Name', 'DOJ', 'AL Used', 'SL Used', 'CL Used', 'Total Days on Leave'])
        for t in trainers:
            leaves = conn.execute('''SELECT leave_type, SUM(days) as total FROM leaves
                                   WHERE trainer_id = ? AND from_date >= ? AND from_date <= ?
                                   GROUP BY leave_type''',
                                 (t['id'], start_date, end_date)).fetchall()
            monthly = {'AL': 0, 'SL': 0, 'CL': 0}
            for l in leaves:
                monthly[l['leave_type']] = l['total']
            total = monthly['AL'] + monthly['SL'] + monthly['CL']
            writer.writerow([t['name'], t['doj'], monthly['AL'], monthly['SL'], monthly['CL'], total])
        conn.close()
        output.seek(0)
        label = start_date + '_to_' + end_date
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Leave_Report_{label}.csv'
        )
    return render_template('admin_download_range.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
