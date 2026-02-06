# Penrose-Lamarck

Live documentation: https://genentech.github.io/penrose-lamarck/

## Getting Started

```sh
 ❯ codex
 ⚠ The penroselamarck MCP server is not logged in. Run `codex mcp login penroselamarck`.

 ⚠ MCP startup incomplete (failed: penroselamarck)
```

```sh
 ❯ codex mcp list
 Name            Url                                        Bearer Token Env Var  Status   Auth
 penroselamarck  http://penroselamarck-api:8080/v1/mcp/sse  -                     enabled  OAuth
```

```sh
 ❯ codex mcp login penroselamarck
 Authorize `penroselamarck` by opening this URL in your browser:
 https://...

 Successfully logged in to MCP server 'penroselamarck'.
```

```sh
 ❯ codex
 /mcp

 🔌  MCP Tools

   • penroselamarck
     • Status: enabled
     • Auth: OAuth
     • URL: http://penroselamarck-api:8080/v1/mcp/sse
     • Tools: auth_login, auth_me, exercise_create, exercise_list, metrics_performance, practice_end, practice_next, practice_start, practice_submit, study_context_get, study_context_set, train_import
     • Resources: (none)
     • Resource templates: (none)
```

```sh
 ❯ codex mcp logout penroselamarck
```

## Contributing

[Fork](https://github.com/genentech/penrose-lamarck/fork) the project, pick an [issue](https://github.com/genentech/penrose-lamarck/issues) and submit a PR! We're looking forward to answering your questions on the issue thread.

## Applicants

If you're applying for a position in our team, having received an invitation from our Talent Partner, you have 7 days to submit your work. Upon a positive assessment, you'll be invited to the next steps of our recruitment process.

We sincerely wish you the best of luck and remain truly appreciative of any time you decide to put aside to working with us.

Yours sincerey,

The Hiring Team
