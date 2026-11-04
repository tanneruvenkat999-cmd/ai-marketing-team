import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import run

class TeamTests(unittest.TestCase):
    def test_demo_and_approval_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=run.run(run.ROOT/'brief.example.json', Path(tmp)/'demo', demo=True)
            self.assertEqual(len(list(p.glob('*.md'))),7)
            self.assertEqual(len((p/'tasks.csv').read_text().splitlines()),8)
            with self.assertRaises(ValueError): run.approve(p,'Reviewer','content')

    @patch.dict('os.environ', {'OPENAI_API_KEY':'test-only'})
    @patch('run.generate',return_value='Draft: needs review')
    def test_live_handoff_and_modified_package(self, generate):
        with tempfile.TemporaryDirectory() as tmp:
            p=run.run(run.ROOT/'brief.example.json', Path(tmp)/'live', model='mock')
            self.assertEqual(generate.call_count,7)
            run.approve(p,'Reviewer','content')
            self.assertEqual(json.loads((p/'approval.json').read_text())['execution'],'manual_only')
            (p/'04_copywriter.md').write_text('Changed content')
            with self.assertRaises(ValueError): run.approve(p,'Reviewer','content')

if __name__=='__main__': unittest.main()
