import urlfinder
from flask import Flask, request, jsonify, redirect
app = Flask(__name__)

domain = "http://wmd.no/"
tracker = urlfinder.Tracker()


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
        return "Exceeded 24 hour limit -- try again later", 403

    uid = urlfinder.url_to_uid(url)
    return jsonify({"url": domain + uid})


@app.route('/<page_id>')
def do_redirect(page_id=None):
    try:
        redirect_url = urlfinder.uid_to_url(page_id)
        urlfinder.increase_accessed(page_id)
    except Exception:
        return "Error"
    else:
        return redirect(redirect_url)
if __name__ == '__main__':
    app.run(debug=True)
