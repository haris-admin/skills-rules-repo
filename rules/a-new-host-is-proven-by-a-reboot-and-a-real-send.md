# A new host or alert path is proven by a reboot and one real send (all agents, all repos)

Applies when an agent builds, resizes or moves a host, a container deploy script, or an email or alert path.

## Why this exists
**14 Nov 2026, HandleDispute move to its own AWS account (OpenSpec 77, 59e):** a frontend deploy passed every stage check, yet after the host was resized (a stop and start) the site stayed down. The deploy script started the live container on a temporary staging network, then deleted that network; a container keeps its start-up network, so Docker could not start it after a reboot. The old production host was deployed by an older script and was not affected, which a read-only check proved. In the same session the alert email path looked finished (identities verified, policy applied) but a real send was denied three times, on the recipient identity, then on the identity's default configuration set, then on an unverified recipient. The alert service swallows errors by design, so only a real send showed it.

## Rules
1. A deploy script is not proven until the host has been stopped and started once with no redeploy and the services return by themselves. Run that reboot on the first host you build, and again after a resize.
2. A container must be created on its permanent network and with a restart policy. A staging network is for checks only; never delete a network that a live container was created on.
3. Docker cannot exec into a restarting or stopped container. A deploy that reloads a proxy must restart it when it is not running cleanly.
4. After finding a defect in a script, check the other hosts deployed by the same script, read only, and report the result before offering a fix.
5. An alert or email path that never raises is proven only by one real send to every recipient, read back from the inbox. A send that returns False is not an answer: print the error.
6. In the SES sandbox the sender needs permission on the recipient identity and on the identity's default configuration set, not only on the sender. Scope them to the account and region and pin the sender with the `ses:FromAddress` condition. Do not write a personal address into the repository.
7. The production build may be older than the code on the working branch: check that a command exists in the running image (`python -m` on the live container) before a deploy script depends on it.
