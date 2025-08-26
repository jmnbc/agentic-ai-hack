# Challenge 5: Agent Orchestration

**Expected Duration:** 60 minutes

## Introduction
By this point we have created **the three agents** and have seen how to evaluate and observe one specific agent. As you know, our use case is a bit more complex and, therefore, we will now create the rest of our architecture to actually make it a multi-agent architecture and not just 3 separate agents. The key word for this challenge will be **Orchestration**.

## What's orchestration and what types are there?
Orchestration in AI agent systems is the process of coordinating multiple specialized agents to work together on complex tasks that a single agent cannot handle alone. It helps break down problems, delegate work efficiently, and ensure that each part of a workflow is managed by the agent best suited for it. 

Some common Orchestration Patterns are:

| Pattern                  | Simple Description                                                                  |
|--------------------------|------------------------------------------------------------------------------------|
| Sequential Orchestration | Agents handle tasks one after the other in a fixed order, passing results along.   |
| Concurrent Orchestration | Many agents work at the same time on similar or different parts of a task.         |
| Group Chat Orchestration | Agents (and people, if needed) discuss and collaborate in a shared conversation.   |
| Handoff Orchestration    | Each agent works until it can’t continue, then hands off the task to another agent.|
| Magentic Orchestration   | A manager agent plans and assigns tasks on the fly as new needs and solutions arise.|

If you want deeper details into orchestration patterns click on this [link](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns?toc=%2Fazure%2Fdeveloper%2Fai%2Ftoc.json&bc=%2Fazure%2Fdeveloper%2Fai%2Fbreadcrumb%2Ftoc.json) to learn more.

Now you might be wondering... ok great... but, **how do I decide on an Orchestration Pattern?** The answer to that question is mostly related to your use case. 
Let's have a look at the 2 most common Orchestration patterns:

| Pattern                    | Flow                                   |
|----------------------------|----------------------------------------|
| Sequential Orchestration   | Agent A → Agent B → Agent C            |
| Concurrent Orchestration   | Agent A + Agent B + Agent C → Combine Results |

In `Sequential Orchestration` the Agents are dependent on a task performed from the previous agent. This is very common in workflows like document processing or step-by-step procedures. With `Concurrent Orchestration` the agents are not dependent on each other and therefore it makes this a great orchestration for parallel processing, multi-source research and so on.

## Let's come back to our use case...
`Concurrent Orchestration` is the answer for our use case. We will have 3 agents that are each responsible for gathering and processing specialized information on different matters from different datasources in our knowledge base. In this challenge, we will create a 4th agent that is responsible for Orchestrating these 3 agents and create the final output that we need. Please have a look at the table underneath and review how we have created our 3 agents.

| Agent | Function | Data Source/Technology | Implementation |
|-------|----------|----------------------|----------------|
| **Claim Reviewer Agent** | Analyzes insurance claims and damage assessments | Cosmos DB data | Azure AI Agent Service + SK Plugins |
| **Policy Checker Agent** | Validates coverage against insurance policies | Azure AI Search connection | Azure AI Agent Service |
| **Risk Analyzer Agent** | Evaluates risk factors and provides recommendations | Cosmos DB data | Azure AI Agent Service + SK Plugins |
| **Master Orchestrator Agent** | Coordinates the three agents and synthesizes their outputs | Combined Plugins + Tools | Semantic Kernel Orchestration |

### Understanding Implementation Approaches: Azure AI Agent Service vs Semantic Kernel Integration

When building intelligent agents, you have two primary implementation approaches available in the Azure ecosystem. **Azure AI Agent Service with direct tool connections** provides a streamlined, low-code approach where agents are configured through the Azure AI Foundry portal with direct connections to Azure services like Azure AI Search, enabling rapid prototyping and deployment with built-in enterprise features like security, monitoring, and compliance. This approach is ideal for straightforward scenarios where agents need to access specific Azure services without complex custom logic. In contrast, **Azure AI Agents with Semantic Kernel integration** offers a more flexible, code-first approach that combines the enterprise-grade capabilities of Azure AI Agent Service with Semantic Kernel's powerful plugin framework. This hybrid approach allows developers to create custom plugins with complex business logic, advanced data processing capabilities, and sophisticated integrations (like our Cosmos DB plugin for retrieving structured claim data), while still benefiting from Azure's managed infrastructure and security features. The Semantic Kernel approach is particularly valuable when you need custom data transformations, complex orchestration patterns, or when integrating with *non-Azure* services.

## Exercise Guide - Time to Orchestrate!

## Part 1- Create your Semantic Kernel Orchestrator

1. Notice we have created an `agents`folder that contains two documents: `tools.py` that (for now!) only contains the CosmosDB Plugin (which we will import for orchestration) 
2. Notice that in the same folder we also have the `policy_checker.py` file that brins us back to challenge 2 and our first agent. Please have a look at these two files before beggining the exercise.
3. Time to build your orchestrator! Please jump over to `orchestration.ipynb` file for a demonstration on how we will integrated our troop of agents to help us solve our pickle! 


## Part 2 - Now onto automation!

Great! Now that you've built your orchestrator in the Jupyter notebook, it's time to deploy it as a production-ready Azure Function app. We've already prepared the Azure Function infrastructure in the `azure-function-orchestrator` folder.

1. **Start the Function App** (if not already running):
   ```bash
   # Navigate to the function app directory
   cd challenge-5/azure-function-orchestrator
   
   # Start the Azure Functions runtime
   func host start
   ```
   
   Or use the VS Code task: `func: func: host start` from the command palette (Ctrl+Shift+P).


2.  **Testing Your Multi-Agent System**


Now let's test each endpoint to ensure everything is working correctly. Please open another terminal and run the following commands:

Test basic functionality:
```bash
curl -X GET "http://localhost:7071/api/health"
```

Test with orchestrator initialization:
```bash
curl -X GET "http://localhost:7071/api/health?test_orchestrator=true"
```


#### 3. Process Insurance Claims
This is the main endpoint that orchestrates your agents! # Process a specific claim (CL001)

```bash
curl -X GET "http://localhost:7071/api/claim?claim_id=CL001"
```



### 📊 Understanding the Response

When you process a claim, you'll get a comprehensive JSON response containing:

```json
{
  "status": "success",
  "claim_id": "CL001",
  "agent_analyses": [
    {
      "agent_name": "PolicyChecker",
      "analysis": "Coverage analysis results..."
    },
    {
      "agent_name": "ClaimReviewer", 
      "analysis": "Claim validation results..."
    },
    {
      "agent_name": "RiskAnalyzer",
      "analysis": "Risk assessment results..."
    }
  ],
  "comprehensive_analysis": "# Combined multi-agent analysis report...",
  "timestamp": "timestamp_value"
}
```

### 🔧 Troubleshooting

**If the function app won't start:**
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify your Azure credentials are configured
3. Check the terminal output for specific error messages

**If you get authentication errors:**
1. Ensure your Azure credentials are properly configured
2. Check that your environment variables are set correctly
3. Verify your Azure AI and Cosmos DB connections

**If agents aren't responding correctly:**
1. Test the Cosmos DB connection endpoint first
2. Check the logs in the terminal for detailed error messages
3. Verify your AI model deployments are active

### 🎯 Success Indicators

You'll know your system is working correctly when:
- ✅ Health check returns `"status": "healthy"`
- ✅ Cosmos DB test shows available claim IDs
- ✅ Claim processing returns analysis from all three agents
- ✅ Each agent provides specialized analysis (policy coverage, claim validation, risk assessment)
- ✅ The comprehensive analysis combines all agent outputs

### 📈 Testing Different Scenarios

Try processing different claim IDs to see how your agents handle various scenarios:
```bash
# Test different claims to see varied responses
curl -X GET "http://localhost:7071/api/claim?claim_id=CL002"
curl -X GET "http://localhost:7071/api/claim?claim_id=CL003"
curl -X GET "http://localhost:7071/api/claim?claim_id=CL004"
```

**What to Look For:**
- Different risk levels across claims
- Varying policy coverage decisions
- Different claim validation outcomes
- How agents handle different types of incidents

Once you've tested your multi-agent orchestrator locally and confirmed it's working correctly, the next logical step would be to deploy it to Azure for production use. This involves deploying your Azure Function app to Azure Functions in the cloud, which provides enterprise-grade scalability, monitoring, and security features. You would typically use the Azure CLI or Azure DevOps pipelines to deploy your function code, configure environment variables for your Azure AI and Cosmos DB connections, and set up proper monitoring and logging. Azure Functions offers automatic scaling based on demand, built-in authentication and authorization, and seamless integration with other Azure services your agents depend on. Additionally, you could configure Application Insights for detailed telemetry and performance monitoring of your multi-agent system in production.

## Part 3 - Start the integration of several tools with ... MCP Server! 

Now that you have a fully functional multi-agent orchestrator running as an Azure Function, you can extend its capabilities by exposing it as a Model Context Protocol (MCP) server. This allows your insurance claim processing agents to be consumed by AI assistants, development tools, and other applications that support MCP. By leveraging [Azure Functions MCP bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp?pivots=programming-language-python), you can transform your orchestrator into a standardized tool that AI models can discover and use dynamically. The MCP server would expose your agents' capabilities as structured tools - for example, a "process_insurance_claim" tool that accepts claim IDs and returns comprehensive analyses. To make this production-ready, you'd deploy your function behind Azure API Management (APIM) to provide enterprise features like authentication, rate limiting, API versioning, and detailed analytics. APIM acts as a gateway that can transform your function endpoints into MCP-compatible interfaces while providing security policies and monitoring. You can reference the [Azure MCP Functions Python samples](https://github.com/Azure-Samples/remote-mcp-functions-python) to see how to structure your function for MCP compatibility, including proper tool definitions, parameter schemas, and response formatting that AI assistants can understand and utilize effectively.

###  Challenge Yourself!

Pick 1-2 expansion ideas and implement them in your system. Consider:
- Which expansion would have the biggest impact on your insurance use case?
- How can you measure the success of your new capabilities?
- What additional data sources or APIs would make your agents even smarter?
- How might you handle errors or edge cases in your expanded system?

**Pro Tip:** Start with one simple expansion before moving to more complex orchestration patterns!


## 🎯 Conclusion

Congratulations! You've successfully built a multi-agent orchestration system that coordinates three specialized insurance agents through a Master Orchestrator. Your system now handles complete insurance claim processing workflows using concurrent orchestration patterns with Semantic Kernel.

**Key Achievements:**
- Implemented concurrent orchestration for parallel agent processing
- Created a Master Orchestrator that synthesizes outputs from multiple agents
- Built hybrid solutions combining Azure AI Agent Service with custom Semantic Kernel plugins
- Developed a production-ready framework for intelligent insurance claim processing
- Prepared the system for enterprise deployment to Azure Functions with scalability and monitoring capabilities
