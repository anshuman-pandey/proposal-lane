"""Disposable non-root deployment, immutable snapshots and backup recovery."""
import json,secrets,subprocess,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
name='proposal-test-'+secrets.token_hex(5);volume=name+'-data';restored=name+'-restore';key=secrets.token_urlsafe(32);image='proposal-lane-acceptance:local'
def docker(*args):return subprocess.check_output(['docker',*args],text=True).strip()
def call(base,path,token=key,data=None,method=None):
 raw=json.dumps(data).encode() if data is not None else None
 headers={'Authorization':'Bearer '+token}
 if raw:headers['Content-Type']='application/json'
 with urllib.request.urlopen(urllib.request.Request(base+path,data=raw,headers=headers,method=method),timeout=10) as r:return json.load(r)
def denied(base,path,token):
 try:call(base,path,token);raise AssertionError('Revoked access worked')
 except urllib.error.HTTPError as e:assert e.code==401

def ready(container):
 base='http://127.0.0.1:'+docker('port',container,'8095/tcp').rsplit(':',1)[1]
 for _ in range(100):
  try:
   with urllib.request.urlopen(base,timeout=1) as r:
    if r.status==200:return base
  except (OSError,urllib.error.URLError):time.sleep(.1)
 raise RuntimeError('Service failed to start')
def start(container,vol):
 docker('run','-d','--name',container,'--read-only','--tmpfs','/tmp:size=32m','--cap-drop=ALL','--security-opt=no-new-privileges:true','-e','PROPOSAL_OWNER_KEY='+key,'-v',vol+':/data','-p','127.0.0.1::8095',image)
 return ready(container)
try:
 base=start(name,volume);assert docker('exec',name,'id','-u')=='10001'
 body=dict(title='Brand proposal',client='Sample client',scope='Design work',currency='USD',items=[dict(description='Design',quantity='1.5',unit_price='100.01')],discount='0.02',tax_percent='10')
 created=call(base,'/api/proposals',data=body);url='/api/proposals/'+created['id'];share=call(base,url+'/shares',data={'revision':1});view='/api/shared/'+share['id'];original=call(base,view,share['token']);assert original['body']['total_cents']==16500
 revoked=call(base,url+'/shares',data={'revision':1});call(base,url+'/shares/'+revoked['id']+'/revoke',data={});denied(base,'/api/shared/'+revoked['id'],revoked['token'])
 body['title']='Revised draft';call(base,url,data={'revision':1,'body':body},method='PUT')
 docker('restart','-t','1',name);base=ready(name);assert call(base,view,share['token'])==original;assert call(base,url)['revision']==2
 docker('stop','-t','1',name)
 with tempfile.TemporaryDirectory() as tmp:
  source=Path(tmp)/'source.sqlite3';backup=Path(tmp)/'backup.sqlite3';docker('cp',name+':/data/proposal.sqlite3',str(source))
  subprocess.run(['python3',str(ROOT/'scripts/backup.py'),str(source),str(backup)],check=True);assert backup.stat().st_mode & 0o777==0o600
  assert subprocess.run(['python3',str(ROOT/'scripts/backup.py'),str(source),str(backup)],capture_output=True).returncode!=0
  docker('volume','create',restored)
  docker('run','--rm','--user','0','-v',restored+':/data','-v',str(backup)+':/backup:ro',image,'python','-c',"import shutil,os;shutil.copyfile('/backup','/data/proposal.sqlite3');os.chown('/data/proposal.sqlite3',10001,10001);os.chmod('/data/proposal.sqlite3',0o600);os.chown('/data',10001,10001)")
  base=start(name+'-restored',restored);assert call(base,view,share['token'])==original;assert call(base,url)['body']['title']=='Revised draft';denied(base,'/api/shared/'+revoked['id'],revoked['token'])
  body['title']='After recovery';assert call(base,url,data={'revision':2,'body':body},method='PUT')['revision']==3
  try:call(base,url,data={'revision':2,'body':body},method='PUT');raise AssertionError('Stale edit accepted')
  except urllib.error.HTTPError as e:assert e.code==400
  fresh=call(base,url+'/shares',data={'revision':3});assert call(base,'/api/shared/'+fresh['id'],fresh['token'])['body']['title']=='After recovery';assert call(base,view,share['token'])==original
 print('PASS: non-root/read-only service, draft revisions, immutable snapshots and revoked access survive restart/clean-volume restore; fresh edits/shares and stale rejection work')
finally:
 for container in (name,name+'-restored'):subprocess.run(['docker','rm','-f',container],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for vol in (volume,restored):subprocess.run(['docker','volume','rm',vol],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
