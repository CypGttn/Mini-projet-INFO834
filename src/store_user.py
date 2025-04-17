import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def store_user(username, password):
    user_key = f"user:{username}"
    user_data = {
        "username": username,
        "password": password
    }
    # Use hset instead of hmset
    r.hset(user_key, mapping=user_data)
    print(f"User {username} stored successfully.")

if __name__ == "__main__":
    # Example usage
    username = "testuser"
    password = "securepassword"

    store_user(username, password)
