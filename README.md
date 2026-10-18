# SkinSync

COMP365 final project. Amaka Okoro.

SkinSync scores a messy INCI list against a short skin profile. I compare three methods on the same 54 labels I wrote:

1. M1 keyword baseline (`skinsync/baseline.py`)
2. M2 profile-blind lexicon (`profile_blind_score` in `skinsync/scoring.py`)
3. M3 profile-aware scorer (`score_product` in `skinsync/scoring.py`)

None of the three is trained. RapidFuzz cutoff is 94. M3 calls a pair compatible if the score is at least 60 and there is no avoid flag.

This is not medical advice. The four people are fake.

AI on this repo: Claude helped with parser and eval scripts. I wrote the labels, lexicon tags, and penalty table.

## What is in the repo

- `skinsync/catalog.py`: 35 development labels + 19 holdout labels (54 total)
- `skinsync/lexicon.py`: safety tags
- `data/raw/open_beauty_facts_products.json`: cleaned Open Beauty Facts dump
- `skinsync/evaluate_final.py`: the script that prints Table I and Table II
- `skinsync/parse.py`, `skinsync/scoring.py`, `skinsync/baseline.py`

Frozen weights: tag `checkpoint1-frozen-weights` (`b1320b26`). That commit has the penalty table and no holdout labels yet.

## Hardware

CPU only. Linux. Python 3.12.3. No GPU. No API keys.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Repeat Table II

```bash
PYTHONPATH=. python3 -m skinsync.evaluate_final
```

Holdout should print:

```
Table II  holdout unsafe precision / recall / F1  (n=19, 3 unsafe)
M1 Keyword             P=0.286  R=0.667  F1=0.400  acc=0.684  correct=13/19
M2 Blind lexicon       P=0.300  R=1.000  F1=0.462  acc=0.632  correct=12/19
M3 Profile-aware       P=0.750  R=1.000  F1=0.857  acc=0.947  correct=18/19
```

The holdout has 16 compatible pairs and 3 incompatible pairs.

```bash
PYTHONPATH=. python3 -m pytest
```

## Demo

```bash
PYTHONPATH=. python3 -m skinsync prepare
PYTHONPATH=. python3 -m skinsync
```

Open http://127.0.0.1:43173. Speaking outline: `demo/SCRIPT.md`. Record in your own voice. Do not use TTS.

## Paper

IEEE SoutheastCon 2027 regular paper. `paper/skinsync_southeastcon.tex`. Compiled PDF: `reports/Okoro_Amaka_COMP365_Final.pdf`. Overleaf upload zip: `submission/Okoro_Amaka_COMP365_Overleaf.zip`.
