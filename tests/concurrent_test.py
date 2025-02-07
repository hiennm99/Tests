import asyncio
import httpx
import random
import json

# URL của API
API_URL_ADD = "http://127.0.0.1:8000/api/v1/pool/add"
API_URL_QUERY = "http://127.0.0.1:8000/api/v1/pool/query"

# Dữ liệu mẫu cho PoolInput (có thể thay đổi cho phù hợp với dữ liệu của bạn)
def generate_test_add():
    pool_id = random.randint(1, 1000)
    pool_values = [random.uniform(1, 100) for _ in range(200)]  # 200 giá trị ngẫu nhiên trong khoảng từ 1 đến 100
    return {
        "poolId": pool_id,
        "poolValues": pool_values
    }

def generate_test_query():
    pool_id = random.randint(1, 1000)
    percentile = random.randint(1, 100)  # Random percentile từ 1 đến 100
    return {
        "poolId": pool_id,
        "percentile": percentile
    }

async def send_request(client: httpx.AsyncClient, data: dict, url: str):
    """Gửi request POST đến API"""
    response = await client.post(url, json=data)
    print(f"Status Code: {response.status_code}, Response: {response.json()}")

async def test_concurrent_requests():
    """Test 100 request đồng thời với add và query"""
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(100):
            if random.choice([True, False]):  # Chọn ngẫu nhiên giữa add và query
                data = generate_test_add()
                tasks.append(send_request(client, data, API_URL_ADD))
            else:
                data = generate_test_query()
                tasks.append(send_request(client, data, API_URL_QUERY))
        
        # Chạy tất cả các tasks đồng thời
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Chạy test
    asyncio.run(test_concurrent_requests())