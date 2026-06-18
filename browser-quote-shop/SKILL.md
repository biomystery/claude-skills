---
name: browser-quote-shop
description: Use the Playwright MCP browser to collect quotes or prices for one item (insurance, a service, a product) across multiple online providers, then compile a sorted comparison table with a recommendation — handling the hard-won form gotchas (address autocomplete, press-and-hold CAPTCHAs, ng-select multi-selects, expiring element refs, broker engines that auto-pull public records). Use when shopping the same thing across many sites and you want one comparison artifact plus a journal log.
user-invocable: true
---

# Browser Quote Shop

Drives the Playwright MCP browser to shop one item across a list of online providers and produces a single comparison table sorted by price, with a recommendation. Each provider's outcome is classified (live quote / agent-only / not available in state / not eligible) and recorded with its quote ID and callback number. Captures the recurring browser-automation gotchas so they aren't rediscovered every run.

## When to Use

- Shopping the same thing (home/auto insurance, a service, a product) across multiple sites
- You want one comparison artifact, not scattered tabs
- Forms are involved — autocomplete, multi-selects, CAPTCHAs, broker engines

## Step 0: Prerequisites

- Playwright MCP tools available (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_select_option`, `browser_evaluate`, `browser_press_key`).
- Assemble a **reusable profile data sheet once** — every provider asks for the same core facts. For insurance: full address (street / city / state / zip as separate fields), year built, sq ft, construction, roof, foundation, prior coverage amounts, security/safety features, owner info. Reuse it verbatim across all providers.

## Step 1: Per-Provider Loop

For each provider: `browser_navigate` → `browser_snapshot` → fill the form from the profile sheet → reach the rate/result page. Snapshot before each interaction to get current element refs.

## Step 2: Classify and Record the Outcome

Every provider lands in one of these buckets — record the bucket plus any quote ID, callback number, and notes:

| Outcome | What it looks like | Capture |
|---|---|---|
| ✅ Live quote | A price renders | $/yr, quote #, coverage summary, buy/call number |
| Agent-only | "An expert will help you finish" / referral | Quote ID, phone, email confirmation |
| Not available in state | Hard block for the ZIP/state | The stated reason |
| Not eligible | Membership/military/etc. gate | Why ineligible |

## Step 3: Compile the Comparison Table

Write results into a `Clean/` comparison note (sorted by price, live quotes first), with a one-line **conclusion** naming the best option and the saving vs. the incumbent. Put raw call notes / IDs in `Projects/`.

## Step 4: Journal

`date "+%H:%M"`, then add a reverse-chronological entry under the right section linking the comparison note.

## Hard-Won Gotchas (read before automating)

| Gotcha | Fix |
|---|---|
| Combined address string fails | Enter **separate** street / city / state / zip fields; a single "123 St, City, ST 00000" string breaks autocomplete and returns "property not found" |
| "Press & hold" CAPTCHA / bot wall | Cannot be solved programmatically — **hand off to the user**, ask them to complete it, then resume from the next page |
| `ng-select` / custom multi-select dropdown | `browser_type` fails ("not an input"). Open it, then `browser_evaluate` to set the hidden input's value and dispatch `input` event; confirm the filtered option, click it |
| Clicking a checkbox label toggles a neighbor | After toggling, re-snapshot and verify only the intended box changed; un-toggle accidental ones |
| Element refs expire between tool calls | Re-`browser_snapshot` immediately before each click/type to get fresh refs |
| Wrong param name | `browser_click` / `browser_type` use `target` (not `ref`) for the element reference |
| Radio group left unanswered blocks submit | "Show rates" silently fails — scan the snapshot for any required radio still unset (e.g. "How would you like to buy?") |
| Broker / marketplace engines auto-pull public records | Engines like Progressive's Bolt prefill assessor data (year built, roof, sq ft, flooring). **Verify and correct** prefilled fields against the user's real info before getting the rate |
| Market-withdrawal blocks | Some markets (e.g. CA home insurance for certain ZIPs) block most carriers online — record the block reason rather than treating it as a failure |

## Example Invocations

```
/browser-quote-shop home insurance for <address> across Mercury, Farmers, Progressive
```
→ Loops the providers, fills each form from one profile sheet, compiles a sorted comparison note

```
/browser-quote-shop auto insurance, providers: GEICO, Progressive, Mercury
```

## Output

- A `Clean/` comparison note: sorted table + conclusion + savings vs incumbent
- Raw IDs / callback numbers in `Projects/`
- A reverse-chronological journal entry

## Requirements

- Playwright MCP browser tools
- A target vault (or just produce the comparison table inline if no vault)

## Skill Structure

```
browser-quote-shop/
├── SKILL.md
└── README.md
```
