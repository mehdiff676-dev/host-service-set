import os
import time
import subprocess
import sys
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PASSWORD = "XZA"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'py'}

# تخزين عمليات السكربتات قيد التشغيل
running_processes = {}

# إنشاء مجلد uploads إذا ما كانش موجود
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            return redirect('/how-to-use')
    return render_template('login.html')

@app.route('/how-to-use', methods=['GET', 'POST'])
def how_to_use():
    if request.method == 'POST':
        return redirect('/dashboard')
    return render_template('how_to_use.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    message = ""
    if request.method == "POST":
        package_name = request.form.get('package_name')
        message = install_package(package_name)
    
    # الحصول على حالة السكربتات
    script_statuses = {}
    for file in files:
        script_statuses[file] = file in running_processes
    
    return render_template('dashboard.html', files=files, message=message, script_statuses=script_statuses)

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return f"تم تثبيت المكتبة {package_name} بنجاح!"
    except subprocess.CalledProcessError:
        return f"فشل في تثبيت المكتبة {package_name}."

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
    return redirect('/dashboard')

@app.route('/run/<filename>')
def run_script(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'status': 'error', 'message': f'File {filename} not found'})
    
    try:
        # إيقاف السكربت إذا كان يعمل بالفعل
        if filename in running_processes:
            running_processes[filename].terminate()
            del running_processes[filename]
        
        # تشغيل السكربت
        process = subprocess.Popen(['python3', filepath])
        running_processes[filename] = process
        return jsonify({'status': 'running', 'message': f'Script {filename} is running'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop/<filename>')
def stop_script(filename):
    try:
        if filename in running_processes:
            process = running_processes[filename]
            process.terminate()
            process.wait(timeout=5)  # انتظار حتى ينتهي
            del running_processes[filename]
            return jsonify({'status': 'stopped', 'message': f'Script {filename} has been stopped'})
        else:
            return jsonify({'status': 'error', 'message': f'Script {filename} is not running'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/speed')
def speed():
    start = time.time()
    for _ in range(1000000): pass
    end = time.time()
    return f"<h2>Speed Test Done in {end - start:.4f} seconds</h2>"

if __name__ == '__main__':
    # Render يعين المنفذ تلقائيًا داخل المتغير PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)