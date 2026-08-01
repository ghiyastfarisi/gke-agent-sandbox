"""An ADK CodeExecutor backed by the GKE Agent Sandbox warm pool.

ADK ships its own GkeCodeExecutor, but its executor_type="sandbox" path is
written against an older k8s-agent-sandbox API (it calls
SandboxClient(template_name=...) and sandbox.run(), neither of which exist in
0.5.4). This is the ~40-line equivalent against the current SDK.
"""

import base64
import time

from google.adk.code_executors import BaseCodeExecutor
from google.adk.code_executors.code_execution_utils import (
    CodeExecutionInput,
    CodeExecutionResult,
)
from k8s_agent_sandbox import SandboxClient
from k8s_agent_sandbox.exceptions import (
    SandboxRequestError,
    SandboxTemplateNotFoundError,
)
from k8s_agent_sandbox.models import SandboxLocalTunnelConnectionConfig


class SandboxCodeExecutor(BaseCodeExecutor):
    """Runs each code block in a fresh gVisor sandbox from the warm pool."""

    warmpool: str = "python-sandbox-warmpool"
    namespace: str = "default"
    router_namespace: str = "default"

    def _new_sandbox(self, attempts=20, delay=5.0):
        """Retries past the warm-pool adoption race in agent-sandbox 0.5.4.

        On adoption the controller briefly writes Ready=False/TemplateNotFound
        before flipping to Ready=True ~70ms later. The client treats that reason
        as terminal, so a bare call fails most of the time. It deletes the
        orphaned claim on the way out, making a retry safe.

        The same error also appears when the warm pool is empty, which is the
        common case here: each run consumes the pooled sandbox and Autopilot
        needs ~60s to schedule a replacement. Hence the generous budget.
        """
        client = SandboxClient(
            connection_config=SandboxLocalTunnelConnectionConfig(
                router_namespace=self.router_namespace
            )
        )
        for attempt in range(1, attempts + 1):
            try:
                return client.create_sandbox(
                    warmpool=self.warmpool, namespace=self.namespace
                )
            except SandboxTemplateNotFoundError:
                if attempt == attempts:
                    raise
                time.sleep(delay)

    def execute_code(self, invocation_context, code_execution_input: CodeExecutionInput):
        # Shipped as base64 because the runtime's /upload endpoint isn't wired
        # up, and /execute splits args without a shell -- so pipes and quoting
        # only work inside an explicit `sh -c`. base64 is shell-safe.
        blob = base64.b64encode(code_execution_input.code.encode()).decode()
        cmd = f'sh -c "echo {blob} | base64 -d > /tmp/code.py && python3 /tmp/code.py"'

        # A cold sandbox can accept the claim before :8888 is listening, and the
        # port-forward tunnel dies with the failed request -- so a retry needs a
        # whole new sandbox, not just another attempt on this one.
        for attempt in range(1, 4):
            sandbox = self._new_sandbox()
            try:
                result = sandbox.commands.run(cmd, timeout=self.timeout_seconds or 60)
                return CodeExecutionResult(
                    stdout=result.stdout or "", stderr=result.stderr or ""
                )
            except SandboxRequestError:
                if attempt == 3:
                    raise
                time.sleep(5)
            finally:
                sandbox.terminate()
