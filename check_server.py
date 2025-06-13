import redis

try:
    # Connect to the Redis server
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Check server connection
    if r.ping():
        print("✅ Redis server is running and responding (PING successful).")

        # Test setting and getting a key
        r.set("test_key", "Memurai working!")
        value = r.get("test_key")
        print("✅ Successfully SET and GET from Redis:", value)

        # Delete test key
        r.delete("test_key")
        print("✅ Test key deleted.")
    else:
        print("❌ Redis server is not responding to PING.")

except redis.ConnectionError as e:
    print("❌ Could not connect to Redis server. Error:", e)
except Exception as e:
    print("❌ Some other error occurred:", e)
