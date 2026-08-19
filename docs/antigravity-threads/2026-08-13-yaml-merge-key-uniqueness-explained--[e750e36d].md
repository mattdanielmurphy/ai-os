---
title: "YAML Merge Key Uniqueness Explained"
date: "2026-08-13"
conversation_id: "e750e36d03f59bfd"
source: "antigravity"
---

# YAML Merge Key Uniqueness Explained

## User

getting Map keys must be unique[@litellm_config.yaml (42:43)](file:///Users/matt/projects/ai-os/litellm_config.yaml#L42:43) why?

---

## Assistant

You are seeing **"Map keys must be unique"** because you are using the YAML merge key (`<<:`) twice under the same `litellm_params` dictionary block:

YAML

```
<<: *common_params
<<: *deepseek_params  # <-- Redefined key '<<' in the same map

```


In standard YAML, `<<` is treated as a regular dictionary key reserved for merging anchors. In a single YAML map/dictionary, **keys must be unique**. Defining `<<:` twice in the same block creates duplicate `<<` keys.

The Fix

To merge multiple anchors into a single map block in YAML, pass them as a **sequence/list** to a single `<<:` key:

YAML

```
model_list:
  - model_name: deepseek-v4-flash-low
    litellm_params:
      model: openrouter/deepseek/deepseek-v4-flash
      reasoning:
        effort: low
      <<: [*common_params, *deepseek_params]

```


Combining `[*common_params, *deepseek_params]` inside square brackets tells the parser to merge both anchors in order into `litellm_params` without re-declaring the `<<` key.

---
