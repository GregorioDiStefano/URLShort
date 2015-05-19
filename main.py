import urlfinder
import sys
from flask import Flask, request, jsonify, redirect, send_from_directory, \
    render_template

app = Flask(__name__, static_url_path='')

domain = "http://wmd.no/"
tracker = urlfinder.Tracker()


@app.route('/')
def index():
    return render_template('index.html')


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
        return "Exceeded 24 hour limit -- try again later", 403

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
    app.run(debug=True)
