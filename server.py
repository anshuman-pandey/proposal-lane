"""Local authenticated API; no public deployment configured."""
import hmac,os,sqlite3
from flask import Flask,g,request,jsonify,abort
from werkzeug.exceptions import HTTPException
from estimates import Proposals,Invalid,calculate

def create_app(path,owner_key):
    if not isinstance(owner_key,str) or not owner_key.isascii() or len(owner_key)<32:raise ValueError('Set PROPOSAL_OWNER_KEY to at least 32 random ASCII characters.')
    app=Flask(__name__);app.config['MAX_CONTENT_LENGTH']=262144
    def db():
        if 'db' not in g:g.db=Proposals(path)
        return g.db
    def token():
        header=request.headers.get('Authorization','');return header[7:] if header.startswith('Bearer ') else ''
    def owner():
        if not hmac.compare_digest(token().encode(),owner_key.encode()):abort(401,description='Owner access denied.')
    def data():
        body=request.get_json()
        if not isinstance(body,dict):raise Invalid('Expected a JSON object.')
        return body
    @app.teardown_appcontext
    def close(error):
        store=g.pop('db',None)
        if store:store.close()
    @app.after_request
    def headers(r):
        r.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"});return r
    @app.errorhandler(Invalid)
    def invalid(e):return jsonify(error=str(e)),400
    @app.errorhandler(HTTPException)
    def http_error(e):return jsonify(error=e.description),e.code
    @app.errorhandler(sqlite3.OperationalError)
    def unavailable(e):return jsonify(error='Storage unavailable. Please retry.'),503
    @app.get('/')
    def home():return app.send_static_file('index.html')
    @app.get('/api/proposals')
    def listing():
        owner();return jsonify([dict(id=r['id'],revision=r['revision']) for r in db().db.execute('SELECT id,revision FROM proposals ORDER BY rowid DESC')])
    @app.post('/api/estimate')
    def estimate():owner();return jsonify(calculate(data()))
    @app.post('/api/proposals')
    def create():owner();return jsonify(id=db().create(data()),revision=1),201
    @app.get('/api/proposals/<key>')
    def view(key):owner();return jsonify(db().view(key))
    @app.put('/api/proposals/<key>')
    def update(key):
        owner();body=data();return jsonify(revision=db().update(key,body.get('revision'),body.get('body')))
    @app.get('/api/proposals/<key>/shares')
    def shares(key):
        owner();db().view(key)
        return jsonify([dict(r) for r in db().db.execute('SELECT id,revision,created_at,revoked FROM shares WHERE proposal=? ORDER BY rowid DESC',(key,))])
    @app.post('/api/proposals/<key>/shares')
    def share(key):owner();body=data();return jsonify(db().share(key,body.get('revision'))),201
    @app.post('/api/proposals/<key>/shares/<share>/revoke')
    def revoke(key,share):owner();db().revoke(key,share);return jsonify(ok=True)
    @app.get('/api/shared/<share>')
    def shared(share):
        try:result=db().shared(share,token())
        except Invalid:abort(401,description='Share access denied.')
        return jsonify(result)
    return app

if __name__=='__main__':
    os.umask(0o077)
    create_app(os.environ.get('PROPOSAL_DATABASE','proposal.sqlite3'),os.environ.get('PROPOSAL_OWNER_KEY','')).run(host='127.0.0.1',port=8095)
