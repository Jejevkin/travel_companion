from httpx import AsyncClient

http_client: AsyncClient | None = None


async def get_http_client() -> AsyncClient:
    return http_client
