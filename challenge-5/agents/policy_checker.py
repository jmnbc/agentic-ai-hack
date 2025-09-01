import os
from typing import Annotated
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole
from semantic_kernel.functions import kernel_function
from semantic_kernel.agents import AzureAIAgent
from dotenv import load_dotenv

load_dotenv()

class PolicyCheckerWrapper:
    """Wrapper to make Azure AI Agent Service agent work with Semantic Kernel orchestration"""
    
    def __init__(self):
        self.project_client = None
        self.agent = None
        self.setup_agent()
    
    def setup_agent(self):
        """Initialize the Azure AI Agent Service policy checker"""
        # Load environment variables
        project_endpoint = os.environ.get("AI_FOUNDRY_PROJECT_ENDPOINT")
        model_deployment_name = "gpt-4.1-mini"
        sc_connection_id = os.environ.get("AZURE_AI_CONNECTION_ID")
        
        self.project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
        )
        
        # Initialize the Azure AI Search tool
        ai_search = AzureAISearchTool(
            index_connection_id=sc_connection_id,
            index_name="insurance-documents-index",
            query_type=AzureAISearchQueryType.SIMPLE,
            top_k=3,
            filter="",
        )
        
        # Create the agent
        self.agent = self.project_client.agents.create_agent(
            model=model_deployment_name,
            name="policy-checker-wrapper",
            instructions="""
            You are an expert Insurance Policy Checker Agent specialized in analyzing auto insurance policies and validating claim coverage. Your primary responsibilities include:

            **Core Functions:**
            - Analyze insurance policy documents to determine coverage details
            - Validate if specific claims are covered under policy terms
            - Explain policy limits, deductibles, and exclusions
            - Identify coverage gaps or restrictions
            - Provide clear explanations of policy benefits

            **Policy Types You Handle:**
            - Commercial Auto Policies
            - Comprehensive Auto Policies  
            - High Value Vehicle Policies
            - Liability Only Policies
            - Motorcycle Policies

            **Response Format:**
            - Start with a clear coverage determination (COVERED/NOT COVERED/PARTIAL COVERAGE)
            - Provide the specific policy section reference
            - Explain coverage limits and deductibles
            - List any relevant exclusions or conditions
            - Suggest next steps if coverage issues exist
            - Everything in a clear, concise manner in one paragraph.

            **Tone:** Professional, accurate, and helpful. Always be thorough in your analysis while remaining clear and concise.
            """,
            tools=ai_search.definitions,
            tool_resources=ai_search.resources,
        )
    
    @kernel_function(description="Check insurance policy coverage and validate claims")
    def check_policy_coverage(self, query: Annotated[str, "Query about policy coverage or claim validation"]) -> Annotated[str, "Policy coverage analysis result"]:
        """Check policy coverage using the Azure AI Agent Service agent"""
        
        # Create a thread for communication with the agent
        thread = self.project_client.agents.threads.create()
        
        # Send a message to the thread
        message = self.project_client.agents.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content=query,
        )
        
        # Create and process an agent run
        run = self.project_client.agents.runs.create_and_process(
            thread_id=thread.id, 
            agent_id=self.agent.id
        )
        
        if run.status == "failed":
            return f"Policy check failed: {run.last_error}"
        
        # Get the agent's response
        messages = self.project_client.agents.messages.list(
            thread_id=thread.id, 
            order=ListSortOrder.ASCENDING
        )
        
        for message in messages:
            if message.role == MessageRole.AGENT:
                if message.content and len(message.content) > 0:
                    content_item = message.content[0]
                    if content_item.get('type') == 'text' and 'text' in content_item:
                        return content_item['text']['value']
        
        return "No response received from policy checker"

# Create an instance of the wrapper
policy_checker_plugin = PolicyCheckerWrapper()