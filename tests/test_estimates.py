import copy,tempfile,unittest
from estimates import calculate,Invalid,Proposals

def proposal():return dict(title='Brand refresh',client='Sample studio',scope='Design and delivery',currency='USD',items=[dict(description='Design',quantity='1.5',unit_price='100.01')],discount='0.02',tax_percent='10')
class EstimateTests(unittest.TestCase):
 def test_exact_rounding_and_discount_before_tax(self):
  r=calculate(proposal());self.assertEqual((r['subtotal_cents'],r['discount_cents'],r['tax_cents'],r['total_cents']),(15002,2,1500,16500))
 def test_zero_price_allowed(self):
  p=proposal();p.update(discount='0');p['items'][0]['unit_price']='0';self.assertEqual(calculate(p)['total_cents'],0)
 def test_round_each_line_not_aggregate(self):
  p=proposal();p.update(discount='0',tax_percent='0');p['items']=[dict(description='Fraction',quantity='0.5',unit_price='0.01')]*3;self.assertEqual(calculate(p)['total_cents'],3)
 def test_non_decimal_and_excess_precision_rejected(self):
  for bad in [True,1,1.2,'NaN','Infinity','1e3','-1','1.001',' 1','١']:
   p=proposal();p['items'][0]['unit_price']=bad
   with self.assertRaises(Invalid):calculate(p)
 def test_zero_quantity_and_excess_discount_rejected(self):
  p=proposal();p['items'][0]['quantity']='0'
  with self.assertRaises(Invalid):calculate(p)
  p=proposal();p['discount']='200'
  with self.assertRaises(Invalid):calculate(p)
 def test_invalid_currency_structure_and_tax(self):
  for change in [dict(currency='JPY'),dict(items=[]),dict(items=[None]),dict(tax_percent='101'),dict(scope='')]:
   p=proposal();p.update(change)
   with self.assertRaises(Invalid):calculate(p)
 def test_no_mutation(self):
  p=proposal();original=copy.deepcopy(p);calculate(p);self.assertEqual(p,original)
class StorageTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=self.tmp.name+'/db';self.db=Proposals(self.path);self.id=self.db.create(proposal())
 def tearDown(self):self.db.close();self.tmp.cleanup()
 def test_stale_edits_rejected(self):
  self.db.update(self.id,1,proposal())
  with self.assertRaises(Invalid):self.db.update(self.id,1,proposal())
  self.assertEqual(self.db.view(self.id)['revision'],2)
 def test_share_is_immutable(self):
  share=self.db.share(self.id,1);p=proposal();p['title']='Changed';self.db.update(self.id,1,p);self.assertEqual(self.db.shared(share['id'],share['token'])['body']['title'],'Brand refresh')
 def test_stale_share_and_boolean_revision_rejected(self):
  self.db.update(self.id,1,proposal())
  for rev in [1,True]:
   with self.assertRaises(Invalid):self.db.share(self.id,rev)
 def test_revocation_and_scope(self):
  share=self.db.share(self.id,1);other=self.db.create(proposal())
  with self.assertRaises(Invalid):self.db.revoke(other,share['id'])
  with self.assertRaises(Invalid):self.db.shared(share['id'],'bad')
  self.db.revoke(self.id,share['id'])
  with self.assertRaises(Invalid):self.db.shared(share['id'],share['token'])
 def test_persistence_without_plaintext_tokens(self):
  share=self.db.share(self.id,1);self.db.close();self.db=Proposals(self.path);self.assertEqual(self.db.shared(share['id'],share['token'])['revision'],1)
  self.assertNotIn(share['token'],str([dict(row) for row in self.db.db.execute('SELECT * FROM shares')]))
