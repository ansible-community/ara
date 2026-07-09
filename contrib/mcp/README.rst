MCP Server for ARA Records Ansible
==================================

`ARA <https://codeberg.org/ansible-community/ara>`_ Records Ansible playbooks and makes them easier to understand and troubleshoot.

This MCP (Model Context Protocol) server gives LLMs read-only access to the data
recorded by ARA: playbooks, tasks, hosts, results and files.

Models can reason about playbooks to make infrastructure even easier to understand and troubleshoot.

Instructions for agents can be found in `AGENTS.md <https://codeberg.org/ansible-community/ara/src/branch/master/contrib/mcp/AGENTS.md>`_.

.. contents:: Table of Contents
   :local:
   :depth: 2

Why
---

LLMs are competent with Ansible, Python, Jinja and YAML.
They even know about development, system administration and configuration management.

When given the right context, they can analyze playbook runs and provide plausible
troubleshooting steps or optimization suggestions:

- Why did this playbook fail ?
- Is there anything wrong with this host ?
- How can we make this playbook faster ?
- Am I leaking secrets or sensitive information ?
- Can you compare these two playbooks ?

Pasting ``ansible-playbook`` console output into a chat window works, but it's
slow and wasteful: an example failed CI job can easily consume 60 000+ tokens of
context just from the terminal log.

The ARA MCP server returns the same information and much more.
This same example playbook comes back structured, filtered and on demand in under 2 000 tokens.
The model asks for exactly what it needs and nothing more.

Requirements
------------

- A running ARA API server (see `Getting Started <https://codeberg.org/ansible-community/ara#getting-started>`_)
- Python >= 3.10
- The ``httpx`` and ``mcp`` packages

Installation
------------

The MCP server is an optional, standalone and self-contained script included in the ARA source repository.
It is not shipped as part of the ``ara`` package and has its own minimal dependencies.

.. code-block:: bash

   # Clone the repository (or use an existing checkout)
   git clone https://codeberg.org/ansible-community/ara ~/.ara/git/ara
   cd ~/.ara/git/ara

   # Create a dedicated virtualenv
   python3 -m venv .venv
   .venv/bin/pip install httpx mcp

Configuration
-------------

The MCP server is started and managed by MCP clients like llama.cpp, LM Studio, ollama, Claude, etc.

Add an entry to the client's MCP configuration, typically a JSON file:

.. code-block:: json

   {
     "mcpServers": {
       "ara": {
         "command": "/home/user/.ara/git/ara/.venv/bin/python",
         "args": [
           "/home/user/.ara/git/ara/contrib/mcp/ara_mcp.py"
         ],
         "env": {
           "ARA_API_SERVER": "http://127.0.0.1:8000"
         }
       }
     }
   }

Adjust the configuration to match the ara deployment.
When the ARA API server requires authentication, add the optional environment variables:

.. code-block:: json

   {
     "env": {
       "ARA_API_SERVER": "http://127.0.0.1:8000",
       "ARA_API_USERNAME": "your-username",
       "ARA_API_PASSWORD": "your-password"
     }
   }

Tool Catalog
------------

The server advertises 13 tools through the MCP ``list_tools`` call.
They fall into two categories:

Foundation Tools
~~~~~~~~~~~~~~~~

These map directly to ARA API resources. They accept filters and return
structured text summaries.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Tool
     - Description
   * - ``get_playbook``
     - Detailed metadata for a playbook (status, duration, stats, labels).
   * - ``list_playbooks``
     - Paginated list with filters: status, name, path, label, controller, Ansible version.
   * - ``get_task``
     - Single task detail plus optional source code snippet from the file.
   * - ``list_tasks``
     - List tasks filtered by playbook, status, name or module (action).
   * - ``get_host``
     - Host summary (result counts) and key facts (OS, kernel, Python, package manager, SELinux).
   * - ``list_hosts``
     - Hosts list with optional playbook filter.
   * - ``get_result``
     - Full result payload: stdout/stderr, return code, error message, source code snippet.
   * - ``list_results``
     - Filterable by playbook, task, host and status (ok/failed/skipped/unreachable).
   * - ``get_file``
     - Raw file content or a snippet around a specific line with configurable context.
   * - ``list_files``
     - List of files recorded for a playbook.

Wrapper Tools
~~~~~~~~~~~~~

These aggregate multiple API calls into a single, higher-level response
tailored for common workflows.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Tool
     - Description
   * - ``troubleshoot_playbook``
     - Aggregates failures, code context, host facts and a summary for LLM-driven debugging.
   * - ``troubleshoot_host``
     - Host-centric failure view (failed + unreachable results) with brief error excerpts.
   * - ``analyze_performance``
     - Cross-run timing analysis, slowest tasks, variance detection and optimization suggestions.

All tools return plain text designed to be understood by LLMs. While ARA's API
returns JSON, these responses are formatted as human and model-readable text to
minimize token usage.

Compatibility
-------------

The MCP server is designed to work with any MCP-compatible client, whether local
or cloud-hosted:

- **Local runtimes**: llama.cpp, Ollama, LM Studio
- **Cloud services**: Claude, ChatGPT, Gemini, Copilot
- **Development tools**: Claude Code, VS Code with MCP extensions, Cursor

It also works with any model that supports tool use, including open-weight
models like Qwen3, Devstral, GLM and GPT-OSS.

See also
--------

- `AGENTS.md <AGENTS.md>`_ — guidance for AI agents on how to best use these tools
- `ARA documentation <https://ara.readthedocs.io>`_
- `ARA API reference <https://demo.recordsansible.org/api/v1/>`_
- `MCP specification <https://modelcontextprotocol.io>`_
