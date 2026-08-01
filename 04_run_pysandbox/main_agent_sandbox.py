import time

from k8s_agent_sandbox import SandboxClient
from k8s_agent_sandbox.exceptions import SandboxTemplateNotFoundError
from k8s_agent_sandbox.models import SandboxLocalTunnelConnectionConfig

WARMPOOL = "python-sandbox-warmpool"
NAMESPACE = "default"

# The router Service lives in `default`, not the client's `agent-sandbox-system`
# default, so router_namespace has to be set explicitly. Port-forward mode is
# required from a laptop: a *.svc.cluster.local URL is only resolvable in-cluster.
client = SandboxClient(
    connection_config=SandboxLocalTunnelConnectionConfig(router_namespace="default")
)

def create_sandbox_with_retry(attempts=5, delay=1.0):
    """Work around a warm-pool adoption race in agent-sandbox v0.5.4.

    On adoption the controller briefly writes Ready=False/TemplateNotFound
    before flipping to Ready=True ~70ms later. The client treats that reason as
    terminal and aborts, so roughly 3 of 4 calls fail. It deletes the orphaned
    claim on the way out, so simply retrying is safe.
    """
    for attempt in range(1, attempts + 1):
        try:
            return client.create_sandbox(warmpool=WARMPOOL, namespace=NAMESPACE)
        except SandboxTemplateNotFoundError:
            if attempt == attempts:
                raise
            time.sleep(delay)


sandbox = create_sandbox_with_retry()
try:
    result = sandbox.commands.run("ls -la")
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
finally:
    sandbox.terminate()
