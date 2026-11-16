"""Exact decimal estimates and immutable, revocable proposal snapshots."""
import hashlib,hmac,json,re,secrets,sqlite3
from decimal import Decimal,ROUND_HALF_UP
from datetime import datetime,timezone
class Invalid(ValueError):pass

def text(value,limit):
    if not isinstance(value,str) or not value.strip() or len(value)>limit or any(ord(c)<32 and c not in '\n\t' for c in value):raise Invalid('Text is missing, invalid or too long.')
    return value.strip()
def number(value,places,maximum):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9]{1,9}(?:\.[0-9]{1,'+str(places)+r'})?',value):raise Invalid('Use a plain nonnegative decimal within the supported precision.')
    result=Decimal(value)
    if result>maximum:raise Invalid('Amount exceeds the supported limit.')
    return result
def cents(value):return int((value*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
def calculate(body):
    if not isinstance(body,dict):raise Invalid('Expected a proposal object.')
    currency=body.get('currency')
    if currency not in ('USD','EUR','GBP','CAD','AUD'):raise Invalid('Choose a supported two-decimal currency.')
    result={key:text(body.get(key),limit) for key,limit in [('title',200),('client',200),('scope',20000)]};result['currency']=currency
    items=body.get('items')
    if not isinstance(items,list) or not 1<=len(items)<=100:raise Invalid('Choose 1 to 100 line items.')
    result['items']=[]
    for item in items:
        if not isinstance(item,dict):raise Invalid('Invalid line item.')
        label=text(item.get('description'),500);quantity=number(item.get('quantity'),3,Decimal('1000000'));price=number(item.get('unit_price'),2,Decimal('1000000'))
        if quantity<=0:raise Invalid('Quantity must be positive.')
        amount=cents(quantity*price)
        result['items'].append(dict(description=label,quantity=str(quantity),unit_price=str(price),amount_cents=amount))
    subtotal=sum(item['amount_cents'] for item in result['items'])
    if subtotal>100000000000:raise Invalid('Proposal total exceeds the supported limit.')
    discount=number(body.get('discount','0'),2,Decimal('1000000000'));discount_cents=cents(discount)
    if discount_cents>subtotal:raise Invalid('Discount cannot exceed subtotal.')
    rate=number(body.get('tax_percent','0'),2,Decimal('100'));tax=int((Decimal(subtotal-discount_cents)*rate/100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    result.update(subtotal_cents=subtotal,discount=str(discount),discount_cents=discount_cents,tax_percent=str(rate),tax_cents=tax,total_cents=subtotal-discount_cents+tax)
    return result

def digest(token):return hashlib.sha256(token.encode()).hexdigest()
class Proposals:
    """All methods except shared require owner authentication at the HTTP boundary."""
    def __init__(self,path):
        self.db=sqlite3.connect(path);self.db.row_factory=sqlite3.Row;self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY,revision INTEGER,body TEXT);
        CREATE TABLE IF NOT EXISTS shares(id TEXT PRIMARY KEY,proposal TEXT REFERENCES proposals(id),revision INTEGER,body TEXT,token_hash TEXT,created_at TEXT,revoked INTEGER DEFAULT 0);''')
    def close(self):self.db.close()
    def create(self,body):
        result=calculate(body);key=secrets.token_urlsafe(16)
        with self.db:self.db.execute('INSERT INTO proposals VALUES(?,1,?)',(key,json.dumps(result)))
        return key
    def view(self,key):
        row=self.db.execute('SELECT * FROM proposals WHERE id=?',(key,)).fetchone()
        if row is None:raise Invalid('Proposal not found.')
        return dict(id=key,revision=row['revision'],body=json.loads(row['body']))
    def update(self,key,expected,body):
        if type(expected) is not int or expected<1:raise Invalid('Invalid revision.')
        encoded=json.dumps(calculate(body))
        with self.db:
            if not self.db.execute('UPDATE proposals SET revision=revision+1,body=? WHERE id=? AND revision=?',(encoded,key,expected)).rowcount:raise Invalid('Proposal changed. Reload before saving.')
        return expected+1
    def share(self,key,expected):
        if type(expected) is not int:raise Invalid('Invalid revision.')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE');row=self.view(key)
            if row['revision']!=expected:raise Invalid('Proposal changed. Reload before sharing.')
            share=secrets.token_urlsafe(16);token=secrets.token_urlsafe(32)
            self.db.execute('INSERT INTO shares VALUES(?,?,?,?,?,?,0)',(share,key,expected,json.dumps(row['body']),digest(token),datetime.now(timezone.utc).isoformat()))
        return dict(id=share,token=token,revision=expected)
    def shared(self,key,token):
        row=self.db.execute('SELECT * FROM shares WHERE id=?',(key,)).fetchone()
        if row is None or row['revoked'] or not isinstance(token,str) or not hmac.compare_digest(row['token_hash'],digest(token)):raise Invalid('Share access denied.')
        return dict(revision=row['revision'],body=json.loads(row['body']),created_at=row['created_at'])
    def revoke(self,proposal,share):
        with self.db:
            if not self.db.execute('UPDATE shares SET revoked=1 WHERE id=? AND proposal=?',(share,proposal)).rowcount:raise Invalid('Share not found.')
