# Stat Pick

Each case asks a question in words about a column of readings, and the readings
are never shown. The task is to decide which of eight summaries the question is
asking for. The plugin is a standard MCP server over stdio; NanoAgent owns its
launch command, environment, input and output checks and lifecycle.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_question` | Returns a case's question and the column it is about, and how many readings the column holds. Not the readings | `src/plugin/summaries.py` |
| `summarise` | Works out one named summary of a column, whether or not it is the one that answers the question | `src/plugin/summaries.py` |
| `solution` | Returns a case's readings and the summary that answers its question. It is `answer-question`'s reference tool, so no task lists it and the model never sees its output | `src/plugin/summaries.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `answer-question` | Chooses which summary of a column answers a question, and gives its value | `decide`, with `read_question` and `summarise`, against the `solution` reference |

This is a `decide` task, so the model does not write any value itself. It
chooses — which summary, out of the eight in the `Statistic` enum — and
NanoAgent calls the tools and builds the answer from what they return. The
arithmetic is entirely the tool's; the judgement is entirely the model's. That
split is the point: a question like *"two parcels were stuck for weeks and drag
the average far above what anyone actually waits — how long is a typical parcel
delayed?"* has one defensible answer (the median, 2 days, against a mean of
8.7), and no rule in the plugin can pick it.

The four cases each want a different summary, for a different reason:

| Case | Question is about | Answer |
|---|---|---|
| `delivery-delays` | a typical wait, with two extreme outliers present | `median` |
| `class-sizes` | the size that occurs most often, for ordering desks in batches | `mode` |
| `sensor-drift` | how far readings sit from their own average | `spread` |
| `rainfall` | how much fell over the whole month | `total` |

## What makes it checkable

The answer has two parts and they are judged separately. The verifier compares
the chosen summary against the reference's, and then works that summary out
again from the reference's copy of the readings and compares the value. A wrong
choice scores 0; the right choice with a value that is not that summary's
scores 0.5, because the judgement was right and the copy was not.

Values are compared to within one part in a million, relative to the size of
the value, so `61 + 1e-5` passes for a total of 61 while `2 + 1e-5` fails for a
median of 2.

The readings are chosen so that every column has exactly one mode, and so that
the summary a question asks for does not happen to equal any other summary of
the same column. Without the second property a wrong choice could land on the
right number and look like understanding; `tests/test_tables.py` pins it.

## Layout

It has the standard plugin layout, which NanoAgent requires:

```text
.
├── nanoagent.yaml   # manifest (a slimconfig ManifestConfig): id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output: slimconfig Output classes
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env             # needed environment variable names (none here)
├── src/plugin/      # the MCP server (__main__.py, its IMPLEMENTATIONS table), tables.py and the tools
├── tests/           # test_verifier.py and test_tables.py, the design's invariants
├── ui/              # how the page draws the outputs: renderers.js and renderers.css
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier package: checks.py, question.py, summary.py and answer.py
```

`contract.py` types every value: the server builds each call's input into its
class and checks its output against its own, and NanoAgent and the verifier
get the same classes. A failing tool raises, and the MCP server returns an
error result.

`verifier/` is deterministic and imports nothing but `statistics`, `contract`
and its own package. Because it may not import the plugin, it writes the eight
summaries out again and works them out itself: it takes no tool's word for what
a column comes to, including the reference tool's, whose claimed value it
checks against its own readings before using it. `tests/test_tables.py` holds
the two implementations in step across every case and every summary.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
```

NanoAgent passes the folder the plugin may write to as `NANOAGENT_WORKSPACE`.
No tool writes to it: every case is held in `src/plugin/tables.py`, so a run
needs no network and no files.
