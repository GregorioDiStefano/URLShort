import urlfinder
import sys
import bcrypt
from peewee import IntegrityError
from flask import Flask, request, jsonify, redirect, send_from_directory, \
    render_template, session, send_file
from settings import settings
import captcha
import io
from itsdangerous import TimestampSigner
import base64
from validate_email import validate_email
from flask import Flask
from flask_mail import Mail, Message

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
    is_valid_email = validate_email(email)

    if not captcha_success:
        return fail("wrong captcha")

    if email and urlfinder.get_userinfo(email):
        return fail("email already in use")

    if not is_valid_email:
        return fail("not valid email")

    if email and password and captcha_success:
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(8))
        try:
            urlfinder.save_userinfo(email, hashed_password)
        except IntegrityError:
            return fail("email already in use")

        session.pop("signup_hash", None)
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
    session.pop("user", None)
    return redirect("/")


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


@app.route('/api')
def api():
    url = request.args.get("url", "")
    ip = request.remote_addr
    email_from_session = session.get("user")
    email_from_get = request.args.get("email")

    get_list = request.args.get("list", "")
    passwd_reset = request.args.get("pw_reset", "")

    def limit_exceeded():
        if not tracker.check_access(ip):
            urlfinder.logging.info("%s has exceeded the daily limit" % ip)
            return fail("daily limit exceeded")

    limit_exceeded()

    if url and ~url.find("."):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://%s" % url
        uid = urlfinder.url_to_uid(url, email_from_session or None)
        return jsonify({"url": settings["domain"] + uid})
    elif get_list == "json":
        user_urls = urlfinder.get_user_urls(email_from_session)
        if user_urls:
            return jsonify(urlfinder.get_user_urls(email_from_session))
    elif passwd_reset == "True" and email_from_get:
        setup_password_reset(email_from_get)
        return jsonify({"pass":"check email"})

    return fail("invalid request or error")

def setup_password_reset(email):
    if email and urlfinder.get_userinfo(email):
        s = TimestampSigner(settings["secret_key"])
        signed_string_b64 = base64.b64encode(s.sign(email))

        msg = Message(body="Hi,\nYou requested a password reset.\nHere is your reset link: " + settings["domain"] + "?token=" + signed_string_b64 + "#reset",
                        subject="Password reset",
                        recipients=[email])
        mail.send(msg)


@app.route('/reset', methods=["POST"])
def do_password_reset():
        try:
            token = str(request.form.get('token', ""))
            new_password = str(request.form.get('new_password', ""))
            token = base64.b64decode(token)
        except Exception, e:
            urlfinder.logging.error(e)
            return fail("error decoding token")

        if token and new_password:
            try:
                s = TimestampSigner(settings["secret_key"])
                result = s.unsign(token, max_age=60*60*24)
                hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt(8))
                urlfinder.update_password(result, hashed_password)
            except Exception, e:
                urlfinder.logging.error(e)
                return fail("error resetting password")
            return jsonify({"success": "password reset"})


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


app.secret_key = settings["secret_key"]

if settings["production"]:
	app.config.update(
	    MAIL_SERVER=settings["MAIL_SERVER"],
	    MAIL_PORT=settings["MAIL_PORT"],
	    MAIL_USE_SSL=settings["MAIL_USE_SSL"],
	    MAIL_USERNAME=settings["MAIL_USERNAME"],
	    MAIL_PASSWORD=settings["MAIL_PASSWORD"],
	    MAIL_DEFAULT_SENDER=settings["MAIL_DEFAULT_SENDER"],
	    )
	mail=Mail(app)

if not settings["production"]:
    app.debug = True


