from flask import Flask, render_template, request, jsonify, abort, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from metrics import uptime_range, incidents_range, response_time_stats, response_time_series
from uptime import uptime_percent
from monitor import check_site
from database import load_sites, save_sites  # keep for migration
from models import db, User, Site
import json
import os
import threading
import time
from scheduler import run_monitor

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///monitor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def migrate_existing_sites():
    if Site.query.count() > 0:
        return  # already migrated
    sites = load_sites()
    if not sites:
        return
    # Create default user if none
    if User.query.count() == 0:
        default_user = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin'))
        db.session.add(default_user)
        db.session.commit()
    user = User.query.first()
    for site_data in sites:
        site = Site(url=site_data['url'], user_id=user.id)
        site.set_chat_ids(site_data.get('chat_ids', []))
        db.session.add(site)
    db.session.commit()

# Iniciar el scheduler en un hilo separado cuando se inicia la aplicación
with app.app_context():
    db.create_all()
    migrate_existing_sites()

monitor_thread = threading.Thread(target=lambda: run_monitor(app), daemon=True)
monitor_thread.start()
print("[APP] Scheduler iniciado en segundo plano")

# ---------- AUTH ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a simple token (in production, use JWT or similar)
            import secrets
            token = secrets.token_urlsafe(32)
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Recuperación de contraseña - Monitor Pro',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f'Haz clic en este enlace para restablecer tu contraseña: {reset_url}'
            mail.send(msg)
            flash('Se ha enviado un enlace de recuperación a tu email.', 'success')
        else:
            flash('Email no encontrado.')
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # For simplicity, accept any token and reset to a default password
    # In production, validate token properly
    if request.method == 'POST':
        new_password = request.form.get('password')
        # Since we don't have user from token, this is placeholder
        flash('Contraseña restablecida. Contacta al administrador para más ayuda.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# ---------- RAÍZ ----------
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# ---------- CONFIG (frecuencia) ----------
def get_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return int(cfg.get("freq", 60))
    except Exception:
        return 60

@app.route("/config", methods=["POST"])
def config():
    freq = int(request.form.get("freq", 60))
    action = request.form.get("action", "stop")
    cfg = {"freq": freq, "action": action}
    with open("config.json", "w") as f:
        json.dump(cfg, f)
    return jsonify({"status": "success", "action": action, "freq": freq})

@app.route("/config", methods=["GET"])
def config_json():
    return jsonify({"freq": get_config()})

# ---------- SITIOS ----------
@app.route("/sites")
@login_required
def get_sites():
    return jsonify([{'url': s.url, 'chat_ids': s.get_chat_ids()} for s in current_user.sites])

# ---------- AÑADIR SITIO ----------
@app.route("/add", methods=["POST"])
@login_required
def add_site():
    try:
        data_json = request.get_json(silent=True) or {}
        url = (request.form.get("url") or data_json.get("url"))
        chat_ids_input = (request.form.get("chat_ids") or data_json.get("chat_ids"))
        if not url: abort(400, description="URL requerida")
        url = url.strip()
        if not url.startswith(("http://", "https://")): url = "https://" + url

        # parsear chat_ids (lista o texto separado por comas/semicolumnas)
        def to_list(val):
            if not val:
                return []
            if isinstance(val, list):
                arr = val
            else:
                arr = [x.strip() for x in str(val).replace(";", ",").split(",")]
            return [x for x in arr if x]
        chat_ids = to_list(chat_ids_input)

        if len(current_user.sites) >= 3:
            return jsonify({"status": "error", "message": "Maximum 3 sites allowed"}), 400

        if Site.query.filter_by(url=url, user_id=current_user.id).first():
            return jsonify({"status": "ok", "message": "Sitio ya existe"}), 200

        site = Site(url=url, user_id=current_user.id)
        site.set_chat_ids(chat_ids)
        db.session.add(site)
        db.session.commit()
        check_site(site)
        return jsonify({"status": "ok", "message": "Sitio añadido y probado", "chat_ids": chat_ids})
    except Exception as e:
        import traceback; traceback.print_exc()
        abort(500, description=str(e))

# ---------- ELIMINAR SITIO ----------
@app.route("/remove", methods=["POST"])
@login_required
def remove_site():
    try:
        data_json = request.get_json(silent=True) or {}
        url = (request.form.get("url") or data_json.get("url"))
        if not url:
            abort(400, description="URL requerida")
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        site = Site.query.filter_by(url=url, user_id=current_user.id).first()
        if not site:
            abort(404, description="Sitio no encontrado")
        db.session.delete(site)
        db.session.commit()
        return jsonify({"status": "ok", "message": "Sitio eliminado", "url": url})
    except Exception as e:
        abort(500, description=str(e))

# ---------- GESTIÓN DE CHATS TELEGRAM ----------
@app.route("/set-chats", methods=["POST"])
@login_required
def set_chats():
    try:
        data = request.get_json(silent=True) or {}
        url = (data.get("url") or request.form.get("url"))
        chat_ids_input = (data.get("chat_ids") or request.form.get("chat_ids"))
        if not url:
            abort(400, description="URL requerida")
        url = url.strip()
        def to_list(val):
            if not val:
                return []
            if isinstance(val, list):
                arr = val
            else:
                arr = [x.strip() for x in str(val).replace(";", ",").split(",")]
            return [x for x in arr if x]
        chat_ids = to_list(chat_ids_input)
        site = Site.query.filter_by(url=url, user_id=current_user.id).first()
        if not site:
            abort(404, description="Sitio no encontrado")
        site.set_chat_ids(chat_ids)
        db.session.commit()
        return jsonify({"status": "ok", "chat_ids": chat_ids})
    except Exception as e:
        abort(500, description=str(e))

# ---------- CHEQUEO ----------
@app.route("/check", methods=["POST"])
@login_required
def check_site_now():
    data = request.get_json()
    if not data or "url" not in data:
        abort(400, description="URL no proporcionada")
    from urllib.parse import unquote
    url = unquote(data["url"]).strip()
    site = Site.query.filter_by(url=url, user_id=current_user.id).first()
    if not site:
        abort(403, description="Not your site")
    ok = check_site(site)
    return jsonify({"status": "ok" if ok else "fail", "message": "Online" if ok else "Fallido"})

# ---------- MÉTRICAS ----------
@app.route("/metrics/<path:url>")
@login_required
def metrics_data(url):
    from urllib.parse import unquote
    url = unquote(url)
    site = Site.query.filter_by(url=url, user_id=current_user.id).first()
    if not site:
        abort(403)
    days = int(request.args.get("days", 1))
    if days <= 0 or days > 365: days = 1
    return jsonify({
        "uptime": uptime_range(site, days),
        "incidents": incidents_range(site, days),
        "response": response_time_stats(site, days),
        "uptime_percent": uptime_percent(site)
    })

# Nueva ruta: serie temporal de tiempos de respuesta (últimos N minutos)
@app.route("/response-series/<path:url>")
@login_required
def response_series(url):
    from urllib.parse import unquote
    url = unquote(url)
    site = Site.query.filter_by(url=url, user_id=current_user.id).first()
    if not site:
        abort(403)
    minutes = int(request.args.get("minutes", 60))
    if minutes <= 0 or minutes > 24*60:
        minutes = 60
    return jsonify(response_time_series(site, minutes))

# ---------- ERRORES ----------
@app.errorhandler(404)
def not_found(error): return jsonify({"error": "Recurso no encontrado"}), 404
@app.errorhandler(500)
def internal_error(error): return jsonify({"error": "Error interno"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)