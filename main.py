import urlfinder
import sys
import bcrypt
from peewee import IntegrityError
from flask import Flask, request, jsonify, redirect, send_from_directory, \
    render_template, session

app = Flask(__name__, static_url_path='')

settings = {"secret_key": "dd32b57e9270fed256d9bed5603b3dbefd06daf"}
domain = "http://wmd.no/"
tracker = urlfinder.Tracker()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if email and password:
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(8))
        try:
            urlfinder.save_userinfo(email, hashed_password)
        except IntegrityError:
            return jsonify({"fail": "email already in use"})

        return jsonify({"success": "ok"})
    else:
        return jsonify({"fail": "email and/or password are blank"})


@app.route('/login', methods=['POST', 'GET'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if email and password:
        userinfo = urlfinder.get_userinfo(email)
        if userinfo:
            hashed = userinfo.password
            if bcrypt.hashpw(password, hashed) == hashed:
                # password is correct
                session['user'] = email
            else:
                # password is incorrect
                pass
    else:
        return jsonify({"fail": "email and/or password are blank"})


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    return redirect("/")


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route('/api')
def api():
    url = request.args.get('url', "")
    ip = request.remote_addr

    if url.startswith("http://") or url.startswith("https://"):
        pass
    else:
        url = "http://%s" % url

    success = urlfinder.shorturl_already_exists(url)
    if success:
        return jsonify({"url": domain + success.uid})

    if not tracker.check_access(ip):
        urlfinder.logging.info("%s has exceeded the daily limit" % ip)
        response = jsonify({"fail": "daily limit exceeded"})
        response.status_code = 403
        return response

    uid = urlfinder.url_to_uid(url)
    return jsonify({"url": domain + uid})


@app.route('/<page_id>')
def do_redirect(page_id=None):
    try:
        redirect_url = urlfinder.uid_to_url(page_id)
        urlfinder.increase_accessed(page_id)
    except:
        e = sys.exc_info()[0]
        urlfinder.logging.error(e)
        return "Error"
    else:
        return redirect(redirect_url)
if __name__ == '__main__':
    app.secret_key = settings["secret_key"]
    app.run(debug=True)
