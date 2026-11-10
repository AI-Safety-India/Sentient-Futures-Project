"""Prospective explicit-text input contract; not proof of historical server inputs.

HF consumes input_ids; vLLM consumes text through generate(), never chat().
The caller must check the actual backend prompt IDs before accepting a result.
No model, network connection, or paid service is created by this module.
"""
from dataclasses import dataclass
import copy
import hashlib
import json

REVISION = 'c202236235762e1c871ad0ccb60c8ee5ba337b9a'
TEMPLATE_SHA256 = 'a4aee8afcf2e0711942cf848899be66016f8d14a889ff9ede07bca099c28f715'
CONTRACT_VERSION = 'e2-explicit-text-v1'

@dataclass(frozen=True)
class PreparedInput:
    text: str
    input_ids: tuple[int, ...]
    template_sha256: str

    def manifest(self):
        return dict(contract=CONTRACT_VERSION,model_revision=REVISION,
                    template_sha256=self.template_sha256,
                    text_sha256=hashlib.sha256(self.text.encode()).hexdigest(),
                    input_ids_sha256=hashlib.sha256(json.dumps(list(self.input_ids),separators=(',', ':')).encode()).hexdigest(),
                    tokens=len(self.input_ids),history_policy='preserve_logged_reasoning',
                    historical_equivalence_verified=False)

def normalize_request(request):
    request=copy.deepcopy(request)
    for message in request['messages']:
        if message['role'] != 'assistant':
            continue
        if 'reasoning' in message:
            if 'reasoning_content' in message and message['reasoning_content'] != message['reasoning']:
                raise ValueError('Conflicting assistant reasoning fields')
            message['reasoning_content']=message.pop('reasoning')
        if message.get('reasoning_details'):
            raise ValueError('reasoning_details needs an explicit reviewed conversion')
        for call in message.get('tool_calls') or []:
            value=call['function'].get('arguments',{})
            if isinstance(value,str):
                value=json.loads(value) if value.strip() else {}
            if not isinstance(value,dict):
                raise ValueError('Tool arguments must be a JSON object')
            call['function']['arguments']=value
    return request

def prepare_input(request, tokenizer):
    digest=hashlib.sha256(str(tokenizer.chat_template).encode()).hexdigest()
    if digest != TEMPLATE_SHA256:
        raise ValueError('Unapproved chat-template change')
    req=normalize_request(request)
    kwargs=dict(tools=req.get('tools') or None,add_generation_prompt=True)
    text=tokenizer.apply_chat_template(req['messages'],tokenize=False,**kwargs)
    direct=tokenizer.encode(text,add_special_tokens=False)
    templated=tokenizer.apply_chat_template(req['messages'],tokenize=True,**kwargs)
    if hasattr(templated,'keys'):templated=templated['input_ids']
    if list(direct) != list(templated):
        raise ValueError('Text and template tokenization differ')
    return PreparedInput(text,tuple(direct),digest)

def verify_backend_ids(prepared, actual_ids):
    actual=tuple(actual_ids)
    if actual != prepared.input_ids:
        first=next((i for i,(a,b) in enumerate(zip(prepared.input_ids,actual)) if a!=b),min(len(actual),len(prepared.input_ids)))
        raise ValueError(f'Backend input mismatch at token {first}; expected {len(prepared.input_ids)}, got {len(actual)}. Reject output.')

def generate_explicit(llm, prepared, sampling_params):
    """Use only with an already-authorized backend; this function DOES run inference."""
    results=llm.generate(prepared.text,sampling_params=sampling_params,use_tqdm=False)
    if len(results)!=1:raise ValueError('Expected one backend result')
    verify_backend_ids(prepared,results[0].prompt_token_ids)
    return results[0]
