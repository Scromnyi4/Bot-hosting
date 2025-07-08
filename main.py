from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from datetime import datetime, timedelta
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'Scromnyi707g90'  # Измените на реальный секретный ключ

# Конфигурация
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создаем папку для загрузок, если ее нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Время работы бота
start_time = datetime.now()
end_time = start_time + timedelta(hours=48)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BotApp')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Главная страница с статусом бота"""
    remaining_time = end_time - datetime.now()
    remaining_str = str(remaining_time).split('.')[0] if remaining_time.total_seconds() > 0 else "00:00:00"
    
    # Логируем посещение
    logger.info(f"Home page visited. IP: {request.remote_addr}")
    
    return render_template('index.html',
                         start=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                         end=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                         remaining=remaining_str,
                         visitor_ip=request.remote_addr)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Страница загрузки файлов"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Файл успешно загружен', 'success')
            logger.info(f"File uploaded: {filename}")
            return redirect(url_for('upload_file'))
    
    # Получаем список загруженных файлов
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path):
            files.append({
                'name': filename,
                'size': f"{os.path.getsize(path) / 1024:.1f} KB",
                'date': datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
            })
    
    return render_template('upload.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Скачивание загруженных файлов"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/status')
def api_status():
    """API для проверки статуса"""
    remaining_seconds = (end_time - datetime.now()).total_seconds()
    return {
        'status': 'running' if remaining_seconds > 0 else 'stopped',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'remaining_seconds': max(0, remaining_seconds),
        'server_time': datetime.now().isoformat()
    }

@app.errorhandler(404)
def page_not_found(e):
    """Обработка 404 ошибки"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
