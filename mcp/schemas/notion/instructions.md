Notion MCP server. notion_read(operation, payload) runs one read operation and notion_write(operation, payload) one write operation; each tool's operation enum is its complete menu. notion_describe(operation) returns an operation's JSON Schema and a working example; the notion://operations resource lists every operation with a one-line summary.

How to work:
- Find things with search_pages (title search across pages and databases) or query_database. Results are slimmed to id, title, url and a few fields. Every id field also accepts a Notion URL, so paste links as-is.
- Read a page with get_page_markdown for prose, or get_page with include_properties:true for a database row's fields.
- Write prose as markdown: create_page and append_blocks take a `markdown` field (GFM: headings, lists, checkboxes, tables, code). Use raw `children` blocks only for what markdown cannot express.
- A database has one or more data sources. query_database resolves single-source databases itself and filters with where { Status: "Done" }; to create a row use parent { type: "data_source_id", data_source_id } from search results or list_data_sources. Row properties take plain values: { Status: "Done", Due: "2026-01-01", Tags: ["a"] }.
- Batchable operations take payload { items: [...], atomic?, concurrency?, idempotency_key? } and run in one call with per-item results.
- Errors carry code, message and fix plus the slice of the schema you got wrong: correct and retry. A result's warnings list fields that were ignored. Call notion_describe only for complex shapes (property definitions, block trees).
- Archive and delete operations cannot be undone through the API; confirm with the user before running them.