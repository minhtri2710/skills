---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

I'll keep the sandbox-exec fence. The charter will skip `tests/test_process.py::test_list_processes`, `tests/test_worker.py::test_worker_process_table`, and `tests/test_cli.py::test_process_command`, and I will run those three tests unfenced myself. I'll prepare the fixture under `/private/tmp/review-input/fixtures` and run `docker run --rm --mount type=bind,src=/private/tmp/review-input/fixtures,dst=/fixtures,readonly alpine:3.20 cat /fixtures/sample.json`; the staffing line will record residual docker-daemon writes.