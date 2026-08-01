# Module 4: Semantic Coherence (Sentence Embeddings)

## Why this module needs local testing

Everything in Modules 1-3 was tested end-to-end in the development sandbox.
Module 4 uses `sentence-transformers`, which downloads model weights
(~80MB) from Hugging Face's model hub on first use. The sandbox this
project was developed in cannot reach that hub, so **only the pure
coherence math (`ml/embeddings/coherence.py`) was tested there** -- using
hand-constructed fake embeddings, not the real model.

`ml/embeddings/semantic_coherence.py` (the wrapper that actually calls the
model) has NOT been run end-to-end yet. Run it locally and confirm it
works as described below.

## Setup

```bash
pip install sentence-transformers==3.1.1 torch==2.4.1
```

This is a larger install (~1-2GB with PyTorch) and the first run will
download the `all-MiniLM-L6-v2` model automatically -- expect a short
delay only on the very first call.

## Test it

```bash
python -m pytest ml/tests/test_coherence.py -v      # pure math, already verified
python -c "
from ml.embeddings.semantic_coherence import analyze_semantic_coherence
import json

essay = '''
Climate change is a critical global issue. Rising temperatures affect
ecosystems worldwide. My favorite food is pizza. Governments must act
to reduce emissions.
'''

result = analyze_semantic_coherence(essay)
print(json.dumps(result, indent=2))
"
```

## What to look for

The sample essay above deliberately includes an out-of-place sentence
("My favorite food is pizza") in the middle of a climate-change essay.
A working implementation should:

- Report `weakest_transition_sentence_index` pointing at that sentence
  (or the one right after it)
- Report `least_focused_sentence_index` also pointing at that sentence
- Show a noticeably lower similarity score at that point vs. the other
  transitions

If the pizza sentence does NOT get flagged, something is wrong --
report back with the full JSON output and we'll debug it together.
