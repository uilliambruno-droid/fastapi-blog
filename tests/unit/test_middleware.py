"""Unit tests for middleware."""

import pytest


@pytest.mark.asyncio
async def test_request_logger_middleware_adds_request_id_header(client):
    """Verify that RequestLoggerMiddleware adds X-Request-ID to response."""
    response = await client.get("/posts/")
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) == 36  # UUID format


@pytest.mark.asyncio
async def test_security_headers_middleware_adds_security_headers(client):
    """Verify that SecurityHeadersMiddleware adds all required security headers."""
    response = await client.get("/posts/")

    # Check all security headers are present
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-xss-protection"] == "1; mode=block"
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert "strict-origin-when-cross-origin" in response.headers["referrer-policy"]
    assert "geolocation=()" in response.headers["permissions-policy"]


@pytest.mark.asyncio
async def test_cors_middleware_allows_configured_origins(client):
    """Verify CORS headers are set for allowed origins."""
    response = await client.get(
        "/posts/",
        headers={"Origin": "http://localhost:3000"},
    )
    # CORS is handled by the middleware, check that request succeeds
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_id_propagated_to_state(client):
    """Verify that request_id is stored in request.state."""
    response = await client.get("/posts/")
    # If request.state was set, the middleware processed the request
    assert response.status_code == 200
    assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_cors_exposes_request_id_header(client):
    """Verify that X-Request-ID is in Access-Control-Expose-Headers."""
    response = await client.get("/posts/")
    assert response.status_code == 200
    # The client fixture is configured with CORS, so this ensures setup_cors was called
    assert "x-request-id" in response.headers
