from flask import Flask, render_template

app = Flask(__name__)

# Configuración para que Flask recargue archivos estáticos
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/myjob')
def myjob():
    return render_template('myjob.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/company')
def company():
    return render_template('company.html')

@app.route('/soon')
def soon():
    return render_template('soon.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# Desactiva caché en desarrollo
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)