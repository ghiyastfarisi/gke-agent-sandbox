"""ADK agent that writes Python and runs it inside a GKE Agent Sandbox.

Needs a Gemini key in pycode/.env:  GOOGLE_API_KEY=...
"""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

from sandbox_executor import SandboxCodeExecutor

load_dotenv()

agent = LlmAgent(
    name="coder",
    model="gemini-flash-latest",
    instruction="Write one ```python block that prints the answer. Standard library only.",
    code_executor=SandboxCodeExecutor(),
)

runner = InMemoryRunner(agent, app_name="demo")
runner.session_service.create_session_sync(app_name="demo", user_id="u", session_id="s")

message = types.Content(role="user", parts=[types.Part(text="What is 17 factorial?")])

for event in runner.run(user_id="u", session_id="s", new_message=message):
    for part in event.content.parts if event.content else []:
        if part.executable_code:
            print("--- code written by the LLM ---")
            print(part.executable_code.code.strip())
        if part.code_execution_result:
            print("--- output from the gVisor sandbox ---")
            print(part.code_execution_result.output.strip())
