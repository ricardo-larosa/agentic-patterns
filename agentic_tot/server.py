import sys
import os

from llama_agents import (
    AgentService,
    HumanService,
    AgentOrchestrator,
    CallableMessageConsumer,
    ControlPlaneServer,
    ServerLauncher,
    QueueMessage,
)
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.tools import FunctionTool
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI

from llama_index.core.llms import ChatMessage, MessageRole
from llama_agents.message_queues.redis import RedisMessageQueue

# create an agent
def get_the_secret_fact() -> str:
    """Returns the secret fact."""
    return "The secret fact is: A baby llama is called a 'Cria'."


tool = FunctionTool.from_defaults(fn=get_the_secret_fact)

worker1 = FunctionCallingAgentWorker.from_tools(
    tools=[tool], 
    llm=Groq(model="llama3-8b-8192"))
worker2 = FunctionCallingAgentWorker.from_tools(
    system_prompt="You are a helpful assistant that tells dumb fact.",
    llm=Groq(model="llama3-8b-8192"),
    verbose=True)

agent1 = worker1.as_agent()
agent2 = worker2.as_agent()

# create our multi-agent framework components
message_queue = RedisMessageQueue()
# message_queue = RabbitMQMessageQueue()

control_plane = ControlPlaneServer(
    message_queue=message_queue,
    orchestrator=AgentOrchestrator(
        llm=Groq(model="llama3-70b-8192")
        ),
    port=8000,
)
agent_server_1 = AgentService(
    agent=agent1,
    message_queue=message_queue,
    description="Useful for getting the secret fact.",
    service_name="secret_fact_agent",
    host="127.0.0.1",
    port=8002,
)
agent_server_2 = AgentService(
    agent=agent2,
    message_queue=message_queue,
    description="Useful for getting random dumb facts.",
    service_name="dumb_fact_agent",
    host="127.0.0.1",
    port=8003,
)

human_service = HumanService(
    message_queue=message_queue,
    description="Answers queries about math.",
    host="127.0.0.1",
    port=8004,
)

# additional human consumer
def handle_result(message: QueueMessage) -> None:
    print("Got result:", message.data)

human_consumer = CallableMessageConsumer(handler=handle_result, message_type="human")

# launch it
launcher = ServerLauncher(
    [agent_server_1, agent_server_2, human_service],
    control_plane,
    message_queue,
    additional_consumers=[human_consumer],
)

launcher.launch_servers()
