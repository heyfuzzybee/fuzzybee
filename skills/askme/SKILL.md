# AskMe — Pre-Decomposition Interview

> Model-invoked skill. Fired by `/fuzzybee` before decomposition.

## When to invoke

Automatically before `/fuzzybee-decompose` when:
- Problem statement is vague (<10 words)
- User hasn't specified success criteria
- Multiple interpretations are possible
- Domain is unfamiliar

## Interview protocol

Ask all applicable questions before proceeding to decomposition.
Max 5 questions. Stop early if clarity is reached.

### 1. Goal

```
What outcome are we aiming for? What does "done" look like?
```

### 2. Constraints

```
What must NOT change? Any hard deadlines, budgets, or compatibility requirements?
```

### 3. Evidence standard

```
How will we know it works? (test passes, curl returns 200, visual inspection, etc.)
```

### 4. Risk awareness

```
What could go wrong? What's the most likely failure mode?
```

### 5. Scope

```
Is there anything explicitly OUT of scope for this cycle?
```

## When to skip

- Problem is clearly specified (user gave a full spec or issue link)
- Running in spawned/headless mode with structured input
- Debugging a specific error with a stack trace

## Output

Append interview answers to the decomposition prompt as structured context.
