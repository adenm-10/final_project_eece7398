# Output Spec — Part A & Part B (draft v0.2)

## 1. What the assignment actually requires

The JSON examples in the handout are **illustrative only** ("what a populated structured design task *might* look like"). The binding requirements are the prose below. Each is listed with a short tag so the schemas can reference it.

### Part A — Paper-to-design-task extraction
| Tag | Requirement (paraphrasing the handout closely) |
|---|---|
| A1 | Build a reproducible pipeline that turns analog-circuit papers into a **structured, evidence-grounded design task**, using text, tables, and figures. |
| A2 | Identify: **circuit function**, **topology / design assets** (if available), **stated performance goals**, **supply / load / test conditions**, **design variables**. |
| A3 | **Link each extracted item** to its page, section, figure, table, or passage. |
| A4 | Normalize into a **consistent machine-readable format**, including **unit normalization**. |
| A5 | **Distinguish design objectives from fixed constraints and from test conditions.** |
| A6 | **Explicitly label unspecified, ambiguous, or unsupported information** instead of filling it in with assumptions. |
| A7 | Build a manually reviewed reference set of key fields **with source evidence**; compare the pipeline against it on **values, units, and technical meaning**; document unsupported or incorrect extractions. |

Illustrative keys from the handout example: `source`, `circuit_type`, `topology_ref`, `objectives`, `constraints`, `design_variables`, `simulation_conditions`, `evidence`, `missing_information`.

### Part B — Option 1: Block-diagram understanding
| Tag | Requirement |
|---|---|
| B1 | Parse functional block diagrams into **labeled blocks, ports, and directed connections**, with **boundary and hierarchy** information. |
| B2 | Annotate the common test set by hand: blocks, labels, ports, directed connections. |
| B3 | Evaluate **block and port detection**, **directed-edge F1**, and **graph/connectivity correctness**, with a brief error analysis. |
| B4 | *Optional:* produce a **SPICE-style subcircuit skeleton** when connectivity and interfaces are sufficiently specified. |
| B5 | Where enough detail exists, simulate in ngspice and report success, metrics, and spec pass/fail, **separating extraction errors from missing source information**. Where it does not, **document what is missing** and evaluate the structural graph instead. |

Illustrative keys from the handout example: `blocks[{id, label}]`, `signal_edges[{from, to}]`, `power_rails[]`.

**Our convention for both parts:** we keep every handout key with the same name, every key is always present (`null` or `[]` when empty), and we never write a guessed value. The keys we add are justified in §2.2 and §3.2.

---

## 2. Part A schema

One JSON file per (paper, design variant).

### 2.1 JSON Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PartA_DesignTask",
  "type": "object",
  "additionalProperties": false,
  "required": ["source","circuit_type","topology_ref","objectives","constraints",
               "design_variables","simulation_conditions","evidence","missing_information"],
  "properties": {
    "source": {
      "type": "object", "additionalProperties": false,
      "required": ["paper_id","title","doi","year","variant"],
      "properties": {
        "paper_id": {"type": "string"},
        "title":    {"type": "string"},
        "doi":      {"type": ["string","null"]},
        "year":     {"type": ["integer","null"]},
        "variant":  {"type": "string", "default": "main"}
      }
    },
    "circuit_type": {"enum": ["op_amp","ota","ldo","bandgap","voltage_reference","comparator","lna","pa",
                              "mixer","vco","tia","pga_vga","filter","adc","dac","pll","other"]},
    "topology_ref": {
      "type": "object", "additionalProperties": false,
      "required": ["value","figure","status","evidence_ids"],
      "properties": {
        "value":  {"type": ["string","null"]},
        "figure": {"type": ["string","null"]},
        "status": {"$ref": "#/$defs/status"},
        "evidence_ids": {"$ref": "#/$defs/ids"}
      }
    },
    "objectives": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["metric","operator","value","unit","raw","conditions","origin","status","evidence_ids"],
      "properties": {
        "metric":     {"type": "string"},
        "operator":   {"enum": [">=","<=","=","range"]},
        "value":      {"$ref": "#/$defs/value"},
        "unit":       {"type": "string"},
        "raw":        {"type": "string"},
        "conditions": {"type": "object"},
        "origin":     {"enum": ["target_stated","measured","simulated"]},
        "status":     {"$ref": "#/$defs/status"},
        "evidence_ids": {"$ref": "#/$defs/ids"}
      }}},
    "constraints": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["parameter","value","unit","raw","status","evidence_ids"],
      "properties": {
        "parameter": {"type": "string"},
        "value":     {"anyOf": [{"$ref": "#/$defs/value"}, {"type": "string"}]},
        "unit":      {"type": ["string","null"]},
        "raw":       {"type": "string"},
        "status":    {"$ref": "#/$defs/status"},
        "evidence_ids": {"$ref": "#/$defs/ids"}
      }}},
    "design_variables": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["name","kind","component_ref","value","unit","status","evidence_ids"],
      "properties": {
        "name":          {"type": "string"},
        "kind":          {"enum": ["transistor_W_L","bias_current","bias_voltage","resistance",
                                   "capacitance","inductance","other"]},
        "component_ref": {"type": "string"},
        "value":         {"type": ["number","null"]},
        "unit":          {"type": ["string","null"]},
        "status":        {"$ref": "#/$defs/status"},
        "evidence_ids":  {"$ref": "#/$defs/ids"}
      }}},
    "simulation_conditions": {
      "type": "object", "additionalProperties": false,
      "required": ["source_type","corner","temperature_C","analysis","evidence_ids"],
      "properties": {
        "source_type":   {"enum": ["measured","simulated","both",null]},
        "corner":        {"type": ["string","null"]},
        "temperature_C": {"anyOf": [{"type": "number"}, {"type": "null"}, {"$ref": "#/$defs/range"}]},
        "analysis":      {"type": "array", "items": {"enum": ["dc","ac","tran","noise","pss","sp"]}},
        "evidence_ids":  {"$ref": "#/$defs/ids"}
      }
    },
    "evidence": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["id","page","locator","quote"],
      "properties": {
        "id":      {"type": "string"},
        "page":    {"type": ["integer","null"]},
        "locator": {"type": "string", "description": "e.g. 'abstract', 'Sec. IV', 'Table I', 'Fig. 2 caption'"},
        "quote":   {"type": "string"}
      }}},
    "missing_information": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["field","reason","note"],
      "properties": {
        "field":  {"type": "string", "description": "dotted path, e.g. 'constraints.load_capacitance'"},
        "reason": {"enum": ["not_stated","ambiguous","only_in_plot","unsupported"]},
        "note":   {"type": "string"}
      }}}
  },
  "$defs": {
    "status": {"enum": ["stated","derived","ambiguous"]},
    "ids":    {"type": "array", "items": {"type": "string"}},
    "range":  {"type": "object", "required": ["min","max"],
               "properties": {"min": {"type": "number"}, "max": {"type": "number"}}},
    "value":  {"anyOf": [{"type": "number"}, {"$ref": "#/$defs/range"}]}
  }
}
```

### 2.2 Key-by-key reasoning

**Handout keys we kept (✔ means it is in the handout example):**

| Key | Covers | Changes relative to the example, and why |
|---|---|---|
| `source` ✔ | A1 | Added `paper_id`, `doi`, `year`, and `variant`. The example only had a filename. A paper may propose several designs, and the reference set needs a stable key to match each design task against (A7). |
| `circuit_type` ✔ | A2 (function) | Made it an enum, so it is comparable across papers (A4). |
| `topology_ref` ✔ | A2 (topology) | Added `figure`, so the task points to the schematic RoCktNet would extract. |
| `objectives` ✔ | A2 (goals), A5 | Kept `metric`, `operator`, `value`, `unit`. The additions are explained below. |
| `constraints` ✔ | A2 (supply/load), A5 | Kept `parameter`, `value`, `unit`. |
| `design_variables` ✔ | A2 (variables) | Changed from bare strings to objects, so each variable can be tied to a schematic component and given evidence (A3). |
| `simulation_conditions` ✔ | A2 (test conditions), A5 | Kept `corner`, `temperature_C`, `analysis`. |
| `evidence` ✔ | A3 | Changed from one string to a list of quoted spans that every field points at. A single string cannot link *each* item to its source. |
| `missing_information` ✔ | A6 | Changed from bare strings to `{field, reason, note}`. A6 names three distinct cases (unspecified, ambiguous, unsupported), and naming the field makes the list checkable. |

**Sub-keys we added:**

| Added key | Reasoning |
|---|---|
| `evidence_ids` (on every item) | **A3** requires *each* extracted item to be linked to its source, not just the paper as a whole. Pointing at ids avoids repeating the same quote across several fields. |
| `evidence[].quote` | Lets a validator confirm that each value actually appears in the source. This is our main hallucination check, and it also produces the "source evidence" that A7 asks for. |
| `status` (`stated` / `derived` / `ambiguous`) | **A6** forbids presenting assumptions as fact. Values that we compute or convert (`derived`) must be distinguishable from values printed in the paper. "Unspecified" goes to `missing_information` rather than appearing as a value. |
| `raw` | **A4 and A7** require checking that units and meaning survive normalization. Keeping the printed text (`"2.2 mW"`) next to the normalized value (`0.0022` W) makes that check possible. |
| `objectives[].origin` | Papers mostly report **measured results**, not targets. A5 requires keeping goals separate from conditions, and our proposal promised to keep measured results separate from targets. When a measured value becomes a `>=` or `<=` objective, it is marked `origin: measured`, `status: derived`. |
| `objectives[].conditions` | Many specs are only meaningful together with a condition, such as phase noise *at 1 MHz offset* or NF *at 5 GHz*. Without the condition the value loses its technical meaning (A7). |
| `design_variables[].component_ref` | Ties each variable to a component in the topology figure. This stops generic variable lists that the paper never supports (A6). |
| `simulation_conditions.source_type` | The handout's key is named "simulation", but papers mostly report **measured** silicon. This records which kind of condition the entry describes (A5). |
| `missing_information[].reason` | Implements A6's three cases. We split "only shown in a plot" out of "unspecified" because our proposal's risk plan does not read values off plots. |

**Conventions (rules, not keys):**
- **Values are in canonical SI.** Logarithmic units and percentages are kept as printed (dB, dBm, dBc/Hz, %).
- **Metric names come from a small vocabulary kept in code**, e.g. `dc_gain`, `gbw`, `phase_margin`, `noise_figure`, `phase_noise`, `power`. Synonyms such as UGB, UGF, and GBW are all mapped to `gbw`.
- **A missing-information checklist must always be accounted for:** process, supply, temperature, corner, power, plus the key metrics for each circuit type. Each must be either filled in or listed in `missing_information`. This makes A6 gradeable.

---

## 3. Part B schema

One JSON file per diagram, or per sub-panel such as (a) or (b).

### 3.1 JSON Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PartB_BlockDiagram",
  "type": "object",
  "additionalProperties": false,
  "required": ["source","blocks","ports","signal_edges","power_rails",
               "boundaries","ambiguities","missing_information","spice_skeleton"],
  "properties": {
    "source": {
      "type": "object", "additionalProperties": false,
      "required": ["diagram_id","paper_id","figure","image_path","image_size"],
      "properties": {
        "diagram_id": {"type": "string"},
        "paper_id":   {"type": ["string","null"]},
        "figure":     {"type": ["string","null"]},
        "image_path": {"type": "string"},
        "image_size": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2}
      }
    },
    "blocks": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["id","label","kind","bbox","parent"],
      "properties": {
        "id":     {"type": "string", "pattern": "^B[0-9]+$"},
        "label":  {"type": "string"},
        "kind":   {"enum": ["box","amplifier","summing_node","multiplier","other"]},
        "bbox":   {"$ref": "#/$defs/bbox"},
        "parent": {"type": ["string","null"], "description": "boundary id or null"}
      }}},
    "ports": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["id","label","direction","bbox"],
      "properties": {
        "id":        {"type": "string", "pattern": "^P[0-9]+$"},
        "label":     {"type": "string"},
        "direction": {"enum": ["in","out","inout","unknown"]},
        "bbox":      {"$ref": "#/$defs/bbox"}
      }}},
    "signal_edges": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["from","to","direction_source","label"],
      "properties": {
        "from": {"type": "string", "description": "block or port id"},
        "to":   {"type": "string", "description": "block or port id"},
        "direction_source": {"enum": ["arrowhead","port_label","layout_heuristic","none"]},
        "label": {"type": ["string","null"]}
      }}},
    "power_rails": {"type": "array", "items": {"type": "string"}},
    "boundaries": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["id","label","kind","bbox","parent"],
      "properties": {
        "id":     {"type": "string", "pattern": "^H[0-9]+$"},
        "label":  {"type": ["string","null"]},
        "kind":   {"enum": ["chip","subsystem","domain","other"]},
        "bbox":   {"$ref": "#/$defs/bbox"},
        "parent": {"type": ["string","null"]}
      }}},
    "ambiguities": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["element","type","note"],
      "properties": {
        "element": {"type": "string"},
        "type":    {"enum": ["direction_unknown","junction_vs_crossing","endpoint_unresolved","label_unreadable"]},
        "note":    {"type": "string"}
      }}},
    "missing_information": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["item","needed_for","reason"],
      "properties": {
        "item":       {"type": "string"},
        "needed_for": {"enum": ["spice_skeleton","simulation"]},
        "reason":     {"enum": ["not_in_diagram","not_in_paper","proprietary_model"]}
      }}},
    "spice_skeleton": {"type": ["string","null"]}
  },
  "$defs": {
    "bbox": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4,
             "description": "[x1, y1, x2, y2] in image pixels"}
  }
}
```

### 3.2 Key-by-key reasoning

**Handout keys we kept:**

| Key | Covers | Changes relative to the example, and why |
|---|---|---|
| `blocks` ✔ | B1, B3 | Kept `id` and `label`. Added `kind`, `bbox`, and `parent` (explained below). |
| `signal_edges` ✔ | B1, B3 | Kept `from` and `to`. Added `direction_source` and `label`. |
| `power_rails` ✔ | B4 | Kept exactly as in the example, a list of names. The rails become subcircuit pins in the skeleton. |

**Keys we added:**

| Added key | Reasoning |
|---|---|
| `source` | Ties the graph to a specific image file, so the `bbox` coordinates have a frame of reference. Also links a diagram back to its paper, which makes the Part A to Part B cross-check possible. |
| `ports` | **B1, B2, and B3 explicitly require ports and port detection**, yet the example has no port list; it uses bare names like `IN_MINUS` as edge endpoints. Declaring ports means every edge endpoint resolves to a declared object, and port detection can be scored. |
| `blocks[].bbox`, `ports[].bbox` | **B3** asks for *detection* metrics, and those need geometry for matching (IoU against the ground truth). They also let us tell a detection error apart from an OCR error. |
| `blocks[].kind` | Summing nodes, mixers, and amplifier triangles are blocks with no box and often no label. Without this field they would either be dropped or be counted as false positives. |
| `blocks[].parent` + `boundaries` | **B1 requires boundary and hierarchy information.** Boundaries are containers, not blocks, and `parent` records the nesting. |
| `signal_edges[].direction_source` | A reviewer asked us to report directions inferred from layout separately from those given by an arrowhead or label. The value `none` marks an undirected line, so we never guess its direction. |
| `signal_edges[].label` | Edge text such as a signal name or a coefficient (`k1`, `f_div`) is part of the connection's meaning, and it is needed to name nets in the skeleton. |
| `ambiguities` | A reviewer asked that ambiguous connections be kept. This is the Part B counterpart of A6: we record the doubt instead of committing to a guess. |
| `missing_information` | **B5 requires documenting what is missing** when a diagram cannot be simulated. It also separates "the source didn't give it" from "we extracted it wrong". |
| `spice_skeleton` | Optional output **B4**. It is `null` whenever an edge is undirected or has an unresolved endpoint. |

**Conventions (rules, not keys):**
- **Fan-out:** one wire feeding *k* blocks becomes *k* edges.
- **Cycles are allowed.** The graph is a directed graph, not a DAG.
- **A differential pair drawn as one line is one edge.**
- **Power pins are not ports.** They go in `power_rails`.
- **Exporting to the handout format** means keeping `blocks[{id, label}]`, `signal_edges[{from, to}]`, and `power_rails`, and replacing each port id with its label.

---

## 4. Open items
1. Compare §2 against Analog Design Bench's design-task fields, as the reviewer suggested.
2. When the common block-diagram test set is released, confirm its format against §3.
3. Write the validator: schema check, check that every evidence id resolves, check that every value appears in its quote, check that every edge endpoint exists.
