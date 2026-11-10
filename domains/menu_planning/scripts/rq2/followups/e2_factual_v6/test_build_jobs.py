import copy,unittest
import build_jobs as b
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs=b.read(b.OUT/'jobs.json')
        cls.source=[j for j in b.read(b.SOURCE/'jobs.json') if j['split']=='train' and j['objective']=='welfare']
    def test_frozen_inputs(self):self.assertEqual(b.validate(self.jobs,self.source)['jobs'],24)
    def test_label_reversal_rejected(self):
        j=copy.deepcopy(self.jobs)
        for x in j:x['label']=1-x['label']
        with self.assertRaises(AssertionError):b.validate(j,self.source)
    def test_extra_instruction_rejected(self):
        j=copy.deepcopy(self.jobs);j[0]['request']['messages'].append({'role':'user','content':b.FACTS})
        with self.assertRaises(AssertionError):b.validate(j,self.source)
    def test_source_treatment_change_rejected(self):
        j=copy.deepcopy(self.jobs);j[0]['target_metadata']['description']+=' More text.'
        with self.assertRaises(AssertionError):b.validate(j,self.source)
    def test_wrong_position_rejected(self):
        j=copy.deepcopy(self.jobs);j[0]['positions']['pos_b']-=1
        with self.assertRaises(AssertionError):b.validate(j,self.source)
if __name__=='__main__':unittest.main()
