# Science Map — shared data brief

We are building an interactive timeline/citation graph of the most important works in
(a) AI: deep learning, NLP, computer vision, reinforcement learning and
(b) biotechnology. Each researcher owns one FIELD and writes ONE JSON file: an array of entries.

## Entry schema (all keys required unless marked optional)
{
  "id": "vaswani2017attention",        // lowercase: firstauthor surname (ascii, no spaces/hyphens) + year + first significant title word
  "title": "Attention Is All You Need",
  "authors": "Vaswani A, Shazeer N, Parmar N, Uszkoreit J, Jones L, Gomez AN, Kaiser Ł, Polosukhin I", // up to 6 names then "et al."
  "year": 2017,
  "venue": "NeurIPS 2017",            // journal/conference + volume/pages if confidently known
  "domain": "ai" | "bio",
  "field": "<your FIELD, exactly as given>",
  "subfield": "<one of your SUBFIELDS, exactly as given>",
  "type": "paper" | "book" | "patent" | "software" | "dataset" | "milestone",
  "importance": 3 | 2 | 1,             // 3 = field-defining landmark, 2 = major, 1 = notable
  "summary": "One or two sentences: what it introduced and why it matters.",
  "builds_on": ["bahdanau2015neural", "..."],   // 1-5 ids of key predecessor works (direct intellectual lineage). [] only for true origins.
  "doi": "10.xxxx/...",                // OPTIONAL — include ONLY if you are highly confident it is exact
  "arxiv": "1706.03762"                // OPTIONAL — include ONLY if highly confident it is exact
}

## Rules
- Accuracy over volume. Never invent a DOI/arXiv id; omit it if unsure. Titles, authors, years, venues must be real.
- Coverage: from the origins of the field through 2026. Include the canonical landmarks, the important
  intermediate steps that link them, and recent (2023–2026) work. Target 80–110 entries.
- Every non-origin entry should have builds_on links forming a connected lineage. Prefer ids within your file;
  cross-field links should use the ANCHOR ids below exactly (another researcher owns them).
- Use each subfield in your list at least 5 times. Spread entries across time.
- Output: valid JSON array only, written to the path you are given. Validate it with
  `python3 -c "import json;d=json.load(open(PATH));print(len(d))"` and check ids are unique and every
  builds_on id either exists in your file or is in the ANCHOR list.
- If you own an anchor id, you MUST create an entry with exactly that id.

## ANCHOR ids (owner in brackets) — use exactly these spellings
[DL] mcculloch1943logical, rosenblatt1958perceptron, minsky1969perceptrons, rumelhart1986learning,
hochreiter1997long, hinton2006fast, glorot2010understanding, nair2010rectified, srivastava2014dropout,
kingma2015adam, ioffe2015batch, ba2016layer, kingma2014autoencoding, goodfellow2014generative,
sohldickstein2015deep, ho2020denoising, song2021scorebased, kaplan2020scaling, hoffmann2022training,
kipf2017semisupervised, shazeer2017outrageously, paszke2019pytorch
[NLP] bengio2003neural, mikolov2013efficient, sutskever2014sequence, bahdanau2015neural, vaswani2017attention,
devlin2019bert, radford2018improving, radford2019language, brown2020language, raffel2020exploring,
ouyang2022training, wei2022chain, lewis2020retrievalaugmented, touvron2023llama, hu2022lora, rafailov2023direct,
deepseekai2025deepseekr1
[CV] lecun1989backpropagation, lecun1998gradient, lowe2004distinctive, deng2009imagenet, krizhevsky2012imagenet,
simonyan2015very, he2016deep, ren2015faster, long2015fully, ronneberger2015unet, chen2020simple, he2020momentum,
dosovitskiy2021image, radford2021learning, rombach2022high, mildenhall2020nerf, kirillov2023segment
[RL] bellman1957dynamic, sutton1988learning, watkins1992qlearning, williams1992simple, sutton1998reinforcement,
mnih2015human, silver2016mastering, silver2017mastering, schulman2015trust, schulman2017proximal,
christiano2017deep, haarnoja2018soft, levine2016endtoend
[MOLBIO] mendel1866versuche, avery1944studies, watson1953molecular, meselson1958replication, nirenberg1961dependence,
smith1970restriction, cohen1973construction, saiki1985enzymatic, jinek2012programmable, cong2013multiplex,
mali2013rna, komor2016programmable, gaudelli2017programmable, anzalone2019search, gardner2000construction,
elowitz2000synthetic, gibson2010creation
[GENOMICS] sanger1977dna, lander2001initial, venter2001sequence, margulies2005genome, bentley2008accurate,
schena1995quantitative, encode2012integrated, macosko2015highly, klein2015droplet, nurk2022complete,
ståhl → use stahl2016visualization
[THERA] kohler1975continuous, goeddel1979expression, kariko2005suppression, fire1998potent, takahashi2006induction,
thomson1998embryonic, porter2011chimeric, maude2014chimeric, polack2020safe, baden2021efficacy, leach1996enhancement
[COMPSTRUCT] needleman1970general, smith1981identification, altschul1990basic, kendrew1958three, berman2000protein,
anfinsen1973principles, kuhlman2003design, senior2020improved, jumper2021highly, baek2021accurate, rives2021biological,
lin2023evolutionary, dauparas2022robust, watson2023novo, abramson2024accurate
