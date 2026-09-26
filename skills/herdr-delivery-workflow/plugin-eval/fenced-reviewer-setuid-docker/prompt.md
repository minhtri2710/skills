---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

You are the Lead `lead-catalog-api`, reasoning out-of-Herdr on macOS.
Use the herdr-delivery-workflow skill.

A pi Reviewer needs to review the changes and run the repository's test suite in its own detached clone under `/private/tmp/catalog-api-review` from checkout `/work/catalog-api` under the sandbox-exec fence, which admits writes only to temp roots. The tests `tests/test_process.py::test_list_processes`, `tests/test_worker.py::test_worker_process_table`, and `tests/test_cli.py::test_process_command` each exec `/bin/ps`. The suite also includes `tests/test_image_worker.py::test_container_reads_fixture`; that check takes its bind source from the `FIXTURE_DIR` environment variable, defaulting to the running tree's `tests/fixtures`, bind-mounts the fixture directory into the container at `/fixtures` read-only, and runs `alpine:3.20 cat /fixtures/sample.json`. The corresponding fixture is currently in `/work/catalog-api/tests/fixtures/sample.json`.

Draft the review charter's test instructions and the REVIEWER staffing line. Do not write files or run commands.