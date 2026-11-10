import copy
import unittest
from types import SimpleNamespace
from input_contract import normalize_request,PreparedInput,verify_backend_ids,generate_explicit

class InputContractTests(unittest.TestCase):
    def test_preserves_reasoning_and_does_not_mutate_log(self):
        req={'messages':[{'role':'assistant','reasoning':'welfare concern','content':'','tool_calls':[{'function':{'name':'place_order','arguments':'{"option_id":"x"}'}}]}]}
        original=copy.deepcopy(req);out=normalize_request(req)
        self.assertEqual(req,original)
        self.assertEqual(out['messages'][0]['reasoning_content'],'welfare concern')
        self.assertEqual(out['messages'][0]['tool_calls'][0]['function']['arguments'],{'option_id':'x'})

    def test_conflicting_reasoning_is_rejected(self):
        with self.assertRaises(ValueError):normalize_request({'messages':[{'role':'assistant','reasoning':'a','reasoning_content':'b'}]})

    def test_non_object_tool_arguments_rejected(self):
        with self.assertRaises(ValueError):normalize_request({'messages':[{'role':'assistant','tool_calls':[{'function':{'arguments':'[]'}}]}]})

    def test_equal_length_different_tokens_rejected(self):
        with self.assertRaises(ValueError):verify_backend_ids(PreparedInput('x',(1,2,3),'hash'),[1,4,3])

    def test_missing_prefix_suffix_rejected(self):
        with self.assertRaises(ValueError):verify_backend_ids(PreparedInput('x',(1,2,3),'hash'),[1,2])

    def test_explicit_route_and_actual_backend_check(self):
        class Backend:
            def generate(self,text,**kwargs):
                self.text=text
                return [SimpleNamespace(prompt_token_ids=[1,2])]
            def chat(self,*a,**kw):raise AssertionError('Chat route is forbidden')
        backend=Backend();p=PreparedInput('exact history',(1,2),'hash')
        generate_explicit(backend,p,None)
        self.assertEqual(backend.text,p.text)

if __name__=='__main__':unittest.main()
