import asyncio
import asyncpg
import redis

async def test_postgres():
    try:
        conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/cuentamelo")
        await conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, password='cuentamelo_redis')
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing service connectivity...")
    
    # Test PostgreSQL
    postgres_ok = asyncio.run(test_postgres())
    
    # Test Redis
    redis_ok = test_redis()
    
    if postgres_ok and redis_ok:
        print("🎉 All services are healthy and accessible!")
    else:
        print("⚠️ Some services are not accessible") 