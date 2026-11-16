import tempfile,unittest
from server import create_app
from test_estimates import proposal
class HTTPTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.owner={'Authorization':'Bearer '+'x'*48};self.client=create_app(self.tmp.name+'/db','x'*48).test_client()
  r=self.client.post('/api/proposals',json=proposal(),headers=self.owner);self.assertEqual(r.status_code,201);self.id=r.json['id'];self.url='/api/proposals/'+self.id
 def tearDown(self):self.tmp.cleanup()
 def share(self):
  r=self.client.post(self.url+'/shares',json={'revision':1},headers=self.owner);self.assertEqual(r.status_code,201);return r.json
 def test_snapshot_survives_edit_and_can_be_revoked(self):
  share=self.share();url='/api/shared/'+share['id'];headers={'Authorization':'Bearer '+share['token']};old=self.client.get(url,headers=headers).json
  p=proposal();p['items'][0]['unit_price']='200'
  self.assertEqual(self.client.put(self.url,headers=self.owner,json={'revision':1,'body':p}).json['revision'],2)
  self.assertEqual(self.client.get(url,headers=headers).json,old)
  self.assertEqual(self.client.post(self.url+'/shares/'+share['id']+'/revoke',headers=self.owner).status_code,200)
  self.assertEqual(self.client.get(url,headers=headers).status_code,401)
 def test_client_cannot_access_owner_operations(self):
  share=self.share()
  for headers in [{},{'Authorization':'Bearer '+share['token']}]:
   for method,path in [('get','/api/proposals'),('post','/api/proposals'),('post','/api/estimate'),('get',self.url),('put',self.url),('get',self.url+'/shares'),('post',self.url+'/shares'),('post',self.url+'/shares/'+share['id']+'/revoke')]:
    self.assertEqual(getattr(self.client,method)(path,headers=headers).status_code,401)
 def test_cross_share_key_and_query_key_denied(self):
  first=self.share();second=self.share();url='/api/shared/'+second['id']
  self.assertEqual(self.client.get(url,headers={'Authorization':'Bearer '+first['token']}).status_code,401)
  self.assertEqual(self.client.get(url+'?token='+second['token']).status_code,401)
 def test_stale_edit_share_and_invalid_body(self):
  self.client.put(self.url,headers=self.owner,json={'revision':1,'body':proposal()})
  self.assertEqual(self.client.put(self.url,headers=self.owner,json={'revision':1,'body':proposal()}).status_code,400)
  self.assertEqual(self.client.post(self.url+'/shares',headers=self.owner,json={'revision':1}).status_code,400)
  for body in [[],{'revision':True,'body':proposal()},{'revision':2,'body':None}]:
   self.assertEqual(self.client.put(self.url,headers=self.owner,json=body).status_code,400)
 def test_estimate_matches_saved_and_recalculates_supplied_totals(self):
  p=proposal();p['total_cents']=1
  estimate=self.client.post('/api/estimate',headers=self.owner,json=p)
  self.assertEqual(estimate.json['total_cents'],16500);self.assertEqual(estimate.json,self.client.get(self.url,headers=self.owner).json['body'])
 def test_share_listing_omits_credentials(self):
  share=self.share();r=self.client.get(self.url+'/shares',headers=self.owner);self.assertEqual(r.json[0]['id'],share['id']);self.assertNotIn(share['token'],r.text);self.assertNotIn('token_hash',r.text)
 def test_limits_and_security_headers(self):
  r=self.client.post('/api/proposals',headers=self.owner,data='x'*262145,content_type='application/json');self.assertEqual(r.status_code,413)
  self.assertEqual(r.headers['Cache-Control'],'no-store');self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff');self.assertIsNone(r.headers.get('Access-Control-Allow-Origin'))
 def test_weak_configuration_rejected(self):
  for value in ['',None,'鍵'*40]:
   with self.assertRaises(ValueError):create_app(self.tmp.name+'/other',value)
