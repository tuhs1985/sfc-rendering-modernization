"""Wait against the controller's gate-relative watchdog, not formal-test time."""
import time


def wait_removed(controller, enforce, gate_observed, max_seconds, deadline,
                 clock=time.monotonic, pause=time.sleep):
    # Gate observation may be slightly later than the controller's gate wakeup.
    # Allow its bounded stop/unload calls after the watchdog; never exceed workflow.
    until=min(deadline,gate_observed+max_seconds+35)
    while controller.poll() is None and clock()<until:
        enforce();pause(.05)
    return controller.poll()
