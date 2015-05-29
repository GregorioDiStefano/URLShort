import urlfinder
import sys
import bcrypt
from peewee import IntegrityError
from flask import Flask, request, jsonify, redirect, send_from_directory, \
    render_template, session, send_file
from settings import settings
import captcha
import io

app = Flask(__name__, static_url_path='')

tracker = urlfinder.Tracker()


def fail(msg):
    msg = {"fail": msg}
    return jsonify(msg), 403


@app.route('/')
def index():
    user_logged_in = False
    if session.get("user", False):
        user_logged_in = session["user"]
    return render_template('index.html', logged_in=user_logged_in)


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    email = str(request.form.get('email'))
    password = str(request.form.get('password'))
    captcha_text = str(request.form.get('captcha'))
    expected_hash = session.get("signup_hash")
    captcha_success = captcha.validate_captcha(captcha_text, expected_hash)

    if not captcha_success:
        return fail("wrong captcha")

    if email and urlfinder.get_userinfo(email):
        return fail("email already in use")

    if email and password and captcha_success:
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(8))
        try:
            urlfinder.save_userinfo(email, hashed_password)
        except IntegrityError:
            return fail("email already in use")

        session.pop("signup_hash")
        session["user"] = email
        return jsonify({"success": "ok"})
    else:
        return fail("email/password blank")


@app.route('/login', methods=['POST', 'GET'])
def login():
    email = str(request.form.get('email', ""))
    password = str(request.form.get('password', ""))
    user_info = urlfinder.get_userinfo(email)

    if email and password and user_info:
        hashed = str(user_info.password)
        if bcrypt.hashpw(password, hashed) == hashed:
            # password is correct
            session["user"] = email
            return jsonify({"pass": "logged in"})

    return jsonify({"fail": "email and/or password are blank"})


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop("user")
    return redirect("/")


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route('/api')
def api():
    url = request.args.get("url", "")
    ip = request.remote_addr
    email = session.get("user")
    get_list = request.args.get("list", "")

    def limit_exceeded():
        if not tracker.check_access(ip):
            urlfinder.logging.info("%s has exceeded the daily limit" % ip)
            return fail("daily limit exceeded")

    limit_exceeded()

    if url:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://%s" % url
        uid = urlfinder.url_to_uid(url, email or None)
        return jsonify({"url": settings["domain"] + uid})
    elif get_list == "json":
        user_urls = urlfinder.get_user_urls(email)
        if user_urls:
            return jsonify(urlfinder.get_user_urls(email))

    return fail("invalid request or error")


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


@app.route('/captcha')
def get_catcha():
    captcha_obj = captcha.make_captcha()
    image_data = io.BytesIO(captcha_obj["image_data"])
    image_hash = captcha_obj["hash"]
    session["signup_hash"] = image_hash
    return send_file(image_data, mimetype='image/gif')


if __name__ == '__main__':
    app.secret_key = settings["secret_key"]

    if not settings["production"]:
        app.debug = True

    app.run()
