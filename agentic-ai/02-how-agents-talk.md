# 02 — How Agents Talk

> Notes on a paper airplane, with a big label on the front so the
> right helper reads them.

---

## The Story

At Anu's bakery, Priya (the froster) needs sprinkles. Her sprinkles
jar is empty.

What does Priya do?

She could **shout**: "I NEED SPRINKLES!"

But then everyone hears. The oven-watcher would get distracted.
The greeter would turn around. The cleaner would stop sweeping.
All for a problem that only concerns the sprinkler.

So instead, Priya writes a little note:

```
┌────────────────────────────────┐
│ TO:    Sprinkler               │
│ FROM:  Priya (Froster)         │
│ TOPIC: SPRINKLES               │
│                                │
│ I'm out. Need a refill by 3pm. │
└────────────────────────────────┘
```

She folds it into a paper airplane and sends it into a special
tray marked **"Messages for Sprinkler."** The sprinkler checks their
tray every minute and sees the note.

Two important things happened:

1. **The note had a big label** that said "SPRINKLES." That way the
   sprinkler knows, just from the label, "this is for me." (If the
   label said "DOUGH," they'd ignore it — or even refuse to open
   it.)
2. **Priya and the sprinkler didn't talk directly.** They used the
   tray. If Priya were replaced by a new helper tomorrow, the
   new helper still knows how the tray works.

This is how agents talk in our project.

---

## What this means for computers

When agents need to share something, they:

1. Put it in a **small labeled box** (called a "message" or an
   "envelope")
2. Hand the box to a **post office** (called a "bus")
3. The post office looks at the label and gives the box to the
   **right helper**

The label has two parts:
- **Who it's for** (an agent's name)
- **What kind of thing is inside** (a "context type" — like
  SPRINKLES, or DOUGH, or GENES)

If the label says "GENES" but the recipient is the sprinkler (who
doesn't know anything about genes), the post office **refuses to
deliver it**. It hands it back and says, "wrong helper."

This "refuse to deliver wrong-kind messages" rule is called a
**scope firewall**. It's one of the most important things that
keeps our system honest.

---

## What we built

In Anukriti, the post office is called the **Agent Message Bus**.
The labeled boxes are called **Agent Context Envelopes**.

Here's what's inside an envelope:

```
┌─────────────────────────────────────┐
│  AgentContextEnvelope               │
│                                     │
│  correlation_id:  abc123            │
│  source_agent:    pharmacogene      │
│  target_agent:    verification      │
│  context_type:    PHARMACOGENE      │  ← the label!
│  payload:         { phenotype: PM } │
│  timestamp:       2026-05-10 12:34  │
│  provenance:      [ ... ]           │
└─────────────────────────────────────┘
```

The `context_type` field is the magic. It can **only** be one of
seven values:

- `POPULATION`
- `GENOTYPE`
- `PHARMACOGENE`
- `EVIDENCE`
- `VERIFICATION`
- `CONFIDENCE`
- `PROVENANCE`

That's it. Those seven. You cannot make a message with
`context_type = "chitchat"` or `context_type = "clinical_advice"`.
The code will stop you.

We call this a **closed enum**. It means "a list that cannot
grow at runtime" — if we ever want to add an eighth kind, a
human has to change the code, and another human has to review
it. No surprises.

The code for the bus lives at:

```
anukriti-swarm/interoperability/agent_bus/
```

And the envelope at:

```
anukriti-swarm/interoperability/shared_context/envelope.py
```

---

## Try it yourself

If you want to see the envelope contract, open:

```
anukriti-swarm/interoperability/shared_context/envelope.py
```

Look for the line that starts with:

```python
class BiomedicalContextType(str, Enum):
```

That's the seven-value closed list. The word `Enum` means "this is
the whole set; no adding later."

Below that, look for:

```python
class AgentContextEnvelope(...):
```

That's the shape of the paper airplane. Every field in there is
required to be on every envelope, every time. No exceptions.

---

## The grown-up version

> Our platform uses an agent message bus (`AgentMessageBus`) as
> the coordination primitive between specialist agents. Messages
> are frozen Pydantic records (`AgentContextEnvelope`) with a
> 7-field required schema:
>
> - `correlation_id` (for tracing)
> - `source_agent`, `target_agent` (routing)
> - `context_type` — a closed 7-value `BiomedicalContextType`
>   enum that enforces scope at message-construction time
> - `payload` (the actual data)
> - `timestamp`
> - `provenance_chain` (a tuple of `ProvenanceStamp` records)
>
> Subscribers register for specific `BiomedicalContextType`
> values, not for agent names. A pharmacogene agent subscribes to
> `PHARMACOGENE` envelopes; a population agent subscribes to
> `POPULATION`. The bus refuses to route mismatched envelopes —
> enforced at delivery time.
>
> This pattern is based on **agent-to-agent (A2A) communication**
> and is a specific implementation of the actor model, scoped to
> biomedical reasoning. Unlike general-purpose message buses, our
> bus cannot carry arbitrary message types — adding a new type
> requires modifying `BiomedicalContextType`, which is a code
> change subject to review.
>
> The bus wraps a legacy `MessageBus` for backward compatibility;
> envelopes are also mirrored onto the legacy bus via
> `.to_message_envelope()`. Non-interop handlers continue working
> unchanged.

---

## What you learned

Before this module: agents talking to each other sounded
magical, maybe involving "AI thinking together."

Now: agents talk like humans sending labeled mail through a post
office. The labels are strict (only seven kinds allowed). The
post office refuses wrong deliveries. That's how we keep a crowd
of helpers from stepping on each other.

---

Next up: **[03 — Who Tells Them What to Do?](03-who-tells-them-what-to-do.md)**

Nine helpers, each with their own job, sending mail. But
**somebody** has to decide who does what today. Let's meet the
boss.
