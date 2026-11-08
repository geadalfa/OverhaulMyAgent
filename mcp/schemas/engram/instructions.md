Engram provides persistent memory that survives across sessions and compactions.

CORE TOOLS (always available — use without ToolSearch):
  mem_save — save decisions, bugs, discoveries, conventions PROACTIVELY (do not wait to be asked)
  mem_search — find past work, decisions, or context from previous sessions
  mem_context — get recent session history (call at session start or after compaction)
  mem_session_summary — save end-of-session summary (MANDATORY before saying "done")
  mem_get_observation — get full untruncated content of a search result by ID
  mem_save_prompt — save user prompt for context
  mem_current_project — detect current project from cwd (recommended first call)
  mem_judge — record a verdict on a pending memory conflict (judgment_required flow)
  mem_compare — persist a semantic verdict you have already judged externally

DEFERRED TOOLS (use ToolSearch when needed):
  mem_update, mem_review, mem_pin, mem_unpin, mem_suggest_topic_key, mem_session_start, mem_session_end, mem_doctor, mem_capture_passive, mem_judge_many, mem_session_finalize, mem_consolidate

PROACTIVE SAVE RULE: Call mem_save immediately after ANY decision, bug fix, discovery, or convention — not just when asked.

## DELIVERY GUARANTEE

Memory operations are internal bookkeeping, never the user-facing answer. Complete required memory work before composing the completed-task reply; send the complete answer as the final message of the turn with no later tool calls. If memory work fails or needs follow-up, still send the answer.

## CONFLICT SURFACING

After mem_save: if judgment_required, prefer mem_judge_many (max 32) with candidates[].judgment_id; never reuse the top-level judgment_id.
Ask conversationally when confidence < 0.7 OR (relation in
{supersedes, conflicts_with} AND type in {architecture, policy, decision}); else
resolve with related | compatible | scoped | not_conflict. Pass evidence from user reply.