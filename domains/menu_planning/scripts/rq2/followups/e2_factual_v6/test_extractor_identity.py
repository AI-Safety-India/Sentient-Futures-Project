import ast,unittest
from pathlib import Path
from analyze_factual import TEMPLATE,REVISION

class ExtractorIdentityTests(unittest.TestCase):
    def test_runner_and_analyzer_share_pinned_identity(self):
        tree=ast.parse((Path(__file__).parent/'extract_factual.py').read_text(encoding='utf-8'))
        assignments={t.id:n.value.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) for t in n.targets if isinstance(t,ast.Name)}
        self.assertEqual(assignments['template_hash'],TEMPLATE)
        self.assertEqual(assignments['revision'],REVISION)
