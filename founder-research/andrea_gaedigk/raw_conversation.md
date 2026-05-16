# Andrea Gaedigk — Raw Conversation
Role: Senior PharmVar Steward | Children's Mercy Kansas City
Date: May 15–16, 2026
Platform: Email (`agaedigk@cmh.edu` ↔ `abhimanyurbsa@gmail.com`)

---

## Initial Outreach

### Abhimanyu — Friday, May 15, 6:26 PM IST
**Subject:** Implementing PharmVar star allele nomenclature in a deterministic PGx engine - a question

Hi Dr. Gaedigk,

Your 2025 StarTRAC-CYP2D6 paper directly shaped how we handle
allele-specific read phasing in our CYP2D6 caller. I wanted to
reach out because PharmVar's nomenclature is the scientific ground
truth our entire engine is built against.

I'm Abhimanyu, building Anukriti — a deterministic pharmacogenomics
inference platform. We implement PharmVar star allele nomenclature
across 13 pharmacogenes (CYP2D6, CYP2C19, CYP2C9, CYP3A5, DPYD,
SLCO1B1 and others) with CPIC-governed phenotype calls,
population-aware reasoning across 5 super-populations, and a
named-refusal taxonomy — when evidence for a specific
ancestry-gene-drug combination is insufficient, we return a named
refusal with a rule ID rather than a confidence-degraded answer.

My question: does PharmVar have a formal pathway for third-party
tools that implement your nomenclature to be acknowledged or listed
as implementers? Even informal guidance on how to stay aligned with
PharmVar updates as we scale would be enormously helpful.

Would you be open to a brief exchange over email?

Best,
Abhimanyu R B

---

### Andrea — Friday, May 15, 7:58 PM IST

Abhimanyu,

We are glad to hear that PharmVar is a useful resource.

If you have a PharmVar account, you have the option to receive an
email notification when a new database version is released.
Otherwise, please be aware of our user terms and conditions
(<https://www.pharmvar.org/terms-and-conditions>). Data can be
retrieved via API (<https://www.pharmvar.org/documentation>). We
also ask users to cite our publications in addition to our website
as citations are measurable while website mentions are rather
difficult to track.

We are currently not having a formal pathway to acknowledge third
party users/implementers as PharmVar is a free resource making this
difficult to track. We are exploring options though.

Thank you
Andrea

*(CMH boilerplate confidentiality footer omitted — standard
"this email is intended only for the addressee" notice.)*

---

## Follow-Up — South Asian PGx Pointers

### Abhimanyu — Friday, May 15, 10:22 PM IST

Hi Andrea,

Thank you so much for the quick response — this is exactly what I
needed.

I'll set up the API integration and register for version
notifications right away. We'll make sure to cite your publications
formally in everything we publish.

One small ask: as someone at the center of the PGx nomenclature
ecosystem, is there anyone you'd suggest I speak with —
particularly around population-specific allele characterization for
South Asian genomes? That's our biggest data gap right now and I
want to make sure we're building on the right foundations.

Thank you again,
Abhimanyu

---

### Andrea — Friday, May 15, 11:56 PM IST

Abhimanyu,

We are rarely receiving submissions from this part of the world.
You may want to contact the senior authors on papers who have
published on the genes of interest.

If you are interested in Thai you may want to contact c. Sukasem at
`chonlaphat.suk@mahidol.ac.th`.

Martin Kennedy has done some work as well — is native New
Zealanders — `martin.kennedy@otago.ac.nz`.

Andrew Somogyi may be able to direct to other people —
`andrew.somogyi@adelaide.edu.au`.

There is unfortunately not much info for the Indian subcontinent.

---

## Closing

### Abhimanyu — Saturday, May 16, 9:08 AM IST

Hi Andrea,

This is incredibly helpful — thank you for taking the time.

Your 2023 pharmacoequity review framed something we'd been building
toward intuitively but hadn't articulated as clearly — the idea that
allele characterization gaps in underrepresented populations aren't
just data problems, they're equity problems with clinical
consequences. That's essentially the founding premise of Anukriti.

The gap in South Asian data being as sparse as it is at the source
level is actually important validation for why we're building this.
I'll reach out to Dr. Sukasem, Dr. Kennedy, and Dr. Somogyi right
away — particularly Dr. Somogyi if he can point toward South
Asian-focused work.

Really appreciate your generosity here.