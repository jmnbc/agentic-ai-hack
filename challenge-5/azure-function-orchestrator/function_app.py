"""
Azure Functions app for Insurance Claim Processing with Semantic Kernel Orchestration
"""

import json
import logging
import asyncio
from typing import Optional
import azure.functions as func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the main function app
app = func.FunctionApp()

# Global orchestrator instance for reuse
_orchestrator: Optional[object] = None

async def get_orchestrator():
    """Get or create the global orchestrator instance."""
    global _orchestrator

    if _orchestrator is None:
        # Lazy import to avoid import-time errors blocking function indexing
        from orchestrator.semantic_orchestrator import InsuranceClaimOrchestrator
        _orchestrator = InsuranceClaimOrchestrator()
        await _orchestrator.initialize()

    return _orchestrator


@app.function_name("process_claim")
@app.route(route="claim", methods=["GET", "POST"], auth_level=func.AuthLevel.FUNCTION)
async def process_claim_http(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for processing insurance claims using semantic kernel orchestration.

    Accepts:
    - GET with query parameters: claim_details, claim_id (optional)
    - POST with JSON body: {"claim_details": "...", "claim_id": "..." (optional)}

    Returns:
    - JSON response with multi-agent analysis results
    """
    logger.info("🚀 Insurance Claim Processing Function triggered")

    try:
        # Extract parameters based on HTTP method
        if req.method == "GET":
            claim_details = req.params.get('claim_details')
            claim_id = req.params.get('claim_id')
        else:  # POST
            try:
                req_body = req.get_json()
                if not req_body:
                    return func.HttpResponse(
                        json.dumps({
                            "status": "error",
                            "error_message": "Request body is required for POST requests"
                        }),
                        status_code=400,
                        mimetype="application/json"
                    )

                claim_details = req_body.get('claim_details')
                claim_id = req_body.get('claim_id')

            except ValueError as e:
                return func.HttpResponse(
                    json.dumps({
                        "status": "error",
                        "error_message": f"Invalid JSON in request body: {str(e)}"
                    }),
                    status_code=400,
                    mimetype="application/json"
                )

        # Validate required parameters - prioritize claim_id for database processing
        if not claim_id and not claim_details:
            return func.HttpResponse(
                json.dumps({
                    "status": "error",
                    "error_message": "Either claim_id or claim_details parameter is required"
                }),
                status_code=400,
                mimetype="application/json"
            )

        # If no claim_id provided, return list of available claim IDs
        if not claim_id:
            return func.HttpResponse(
                json.dumps({
                    "status": "info",
                    "message": "This orchestrator processes claims by ID from the database. Use one of these available claim IDs:",
                    "available_claim_ids": ["CL001", "CL002", "CL003", "CL004"],
                    "example_usage": "?claim_id=CL001",
                    "claim_details_provided": claim_details[:100] + "..." if claim_details and len(claim_details) > 100 else claim_details
                }),
                status_code=200,
                mimetype="application/json"
            )

        logger.info(f"Processing Claim ID: {claim_id}")
        if claim_details:
            logger.info(f"Additional context provided: {claim_details[:100]}{'...' if len(claim_details) > 100 else ''}")

        # Get orchestrator and process claim
        orchestrator = await get_orchestrator()
        result = await orchestrator.process_claim(claim_id)

        # Return success response
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"❌ Error processing claim: {str(e)}")

        error_response = {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__
        }

        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )


@app.function_name("health_check")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for the Azure Function."""

    try:
        # Test basic functionality
        health_status = {
            "status": "healthy",
            "timestamp": str(asyncio.get_event_loop().time()),
            "service": "Insurance Claim Orchestrator",
            "version": "1.0.0"
        }

        # Optionally test orchestrator initialization
        test_orchestrator = req.params.get('test_orchestrator', '').lower() == 'true'

        if test_orchestrator:
            try:
                orchestrator = await get_orchestrator()
                health_status["orchestrator_status"] = "initialized"
            except Exception as e:
                health_status["orchestrator_status"] = f"error: {str(e)}"
                health_status["status"] = "degraded"

        return func.HttpResponse(
            json.dumps(health_status, indent=2),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")

        error_response = {
            "status": "unhealthy",
            "error_message": str(e),
            "timestamp": str(asyncio.get_event_loop().time())
        }

        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )


@app.function_name("test_cosmos_connection")
@app.route(route="test-cosmos", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
async def test_cosmos_connection(req: func.HttpRequest) -> func.HttpResponse:
    """Test Cosmos DB connection endpoint."""

    try:
        from orchestrator.tools import CosmosDBPlugin

        cosmos_plugin = CosmosDBPlugin()
        connection_result = cosmos_plugin.test_connection()

        response = {
            "status": "success",
            "cosmos_test_result": connection_result,
            "timestamp": str(asyncio.get_event_loop().time())
        }

        return func.HttpResponse(
            json.dumps(response, indent=2),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"❌ Cosmos DB test failed: {str(e)}")

        error_response = {
            "status": "error",
            "error_message": str(e),
            "timestamp": str(asyncio.get_event_loop().time())
        }

        return func.HttpResponse(
            json.dumps(error_response),
            status_code=500,
            mimetype="application/json"
        )
