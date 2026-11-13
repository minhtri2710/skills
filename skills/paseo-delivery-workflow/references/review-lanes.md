# Review lanes

Carry rule, build input: a read path that is solely a build input may change when the
product artifact built there (build-VCS stamping off) has the same hash at both SHAs.

## Terminal output

A lane that checks terminal output meant for a human runs under a real pty with explicit
columns and color profile, and its output carries the captured screens.

## Second host

A lane run on a second host holds that host's run lock, which the project's record names
(one run at a time, taken before the run and released after it), never receives real
secrets, and with that host unreachable fails with no local fallback; on an interrupt it
stops the remote run it recorded and confirms it gone before releasing the lock. A
second-host run dies with its runner: the remote wrapper kills its whole process group on
every exit; a periodic heartbeat over the connection turns a dead connection into SIGPIPE,
since a dropped ssh connection with no pty sends no HUP; and, under the run lock before
starting, the runner checks the recorded remote process group for an orphan; with a live
orphan it does not start, the agent running the lane reports the orphan as a `collision`,
and the lane is not green. A SIGKILL of the local runner mid-run proves the whole; it runs
once per change to the remote wrapper, with its output in the project's record.
