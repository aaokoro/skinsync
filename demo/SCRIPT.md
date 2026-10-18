# Demo + paper review (6 to 10 minutes)

Your voice. No TTS. You do not have to be on camera. Have http://127.0.0.1:43173 open.

1. Question (1 min)
   Can a short skin profile plus an INCI list beat a global bad ingredient list? The task is yes/no on product and profile pairs. I did not train a model.

2. Related work (1 min)
   Lee 2024: images and a deep net. Kalicinska 2023: one chemical, Naive Bayes, 86%. Kyaw 2024: TF-IDF similarity, 66.40% cosine, 61.52% Jaccard, 80% on serum and sunscreen. Liu 2024 workshop/preprint: learned attributes beat keywords. My gap is messy INCI plus a named restriction list.

3. Methods, live (2 to 3 min)
   Show Maya + CeraVe (all three say yes). Maya + messy lotion (all no). Alex + retinol (M1 and M2 no, M3 yes). Maya + Aveeno (I said yes, M3 says no). Say the settings: RapidFuzz cutoff 94, compatible if score >= 60 and no avoid flag. Three methods, not three trained models.

4. Results (1 to 2 min)
   Holdout n=19, 16 compatible, 3 incompatible, labeled after I froze the weights (tag checkpoint1-frozen-weights).
   M1 13/19, P/R/F1 0.286 / 0.667 / 0.400.
   M2 12/19, 0.300 / 1.000 / 0.462.
   M3 18/19, 0.750 / 1.000 / 0.857.
   Dev 1.00 is not impressive. I wrote those labels while building the scorer.

5. Why, and the failure (1 to 2 min)
   M3 wins by not counting retinol or acids against someone who can use them.
   M2 is one pair worse than M1 on holdout because of Maya and Priya on Aveeno (isopropyl palmitate and benzyl alcohol), not because of Alex retinol.
   Maya x Aveeno is the holdout miss. Maya x retinol scores 86 and still says good match. I have not tested those fixes.

6. Impact and next steps (1 min)
   A wrong safe score on an allergen is bad. Not a medical device.
   Next: block good match when there is an avoid flag, retag preservative benzyl alcohol, and get a second person to label 50 new pairs.

Upload unlisted. Open the link in a private window before you put it on the supplemental page.
