# SkinSync

COMP365 final project. Amaka Okoro.

SkinSync scores a messy INCI list against a short skin profile. I compare three methods on the same 54 labels I wrote:

1. M1 keyword baseline (`skinsync/baseline.py`)
2. M2 profile-blind lexicon (`profile_blind_score` in `skinsync/scoring.py`)
3. M3 profile-aware scorer (`score_product` in `skinsync/scoring.py`)

None of the three is trained. RapidFuzz cutoff is 94. M3 calls a pair compatible if the score is at least 60 and there is no avoid flag.

This is not medical advice. The four people are fake.

## AI disclosure

I used Claude to help me map out the project and figure out how this GitHub repo should be organized (folders, README sections, what had to be public). I also used it when I got stuck structuring the parser and the evaluation scripts. I wrote the labels, the lexicon tags, and the scoring rules. I recorded the demo in my own voice. I did not use AI to write or polish the paper.

## Demo video

Recorded paper review and live demo: https://youtu.be/l9Ak-LmXw6Y

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
