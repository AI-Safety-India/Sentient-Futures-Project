"""Offline, text-only renderer for the pinned audited Qwen template.

Loads the cached Rust tokenizer and Jinja template directly, avoiding model/
PyTorch imports. Equivalence is checked against saved HF/vLLM token evidence.
This is intentionally not a general multimodal AutoTokenizer replacement.
"""
from pathlib import Path
import json
from tokenizers import Tokenizer
from jinja2.sandbox import ImmutableSandboxedEnvironment

class CachedTextTokenizer:
    def __init__(self, snapshot):
        snapshot=Path(snapshot)
        self.chat_template=(snapshot/'chat_template.jinja').read_text(encoding='utf-8')
        self.backend=Tokenizer.from_file(str(snapshot/'tokenizer.json'))
        env=ImmutableSandboxedEnvironment(trim_blocks=True,lstrip_blocks=True,extensions=['jinja2.ext.loopcontrols'])
        env.filters['tojson']=lambda value,**kw:json.dumps(value,ensure_ascii=False,**kw)
        def fail(message):raise ValueError(message)
        env.globals['raise_exception']=fail
        self.template=env.from_string(self.chat_template)

    def encode(self,text,add_special_tokens=False):
        return self.backend.encode(text,add_special_tokens=add_special_tokens).ids

    def apply_chat_template(self,messages,tools=None,add_generation_prompt=True,tokenize=False):
        if any(m.get('content') is not None and not isinstance(m['content'],str) for m in messages):
            raise ValueError('Only text messages are supported by this audited adapter')
        text=self.template.render(messages=messages,tools=tools,add_generation_prompt=add_generation_prompt)
        return self.encode(text,False) if tokenize else text
