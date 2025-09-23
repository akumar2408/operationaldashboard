import os, rq, redis
def main():
    redis_url = f"redis://{os.getenv('REDIS_HOST','redis')}:{os.getenv('REDIS_PORT','6379')}"
    conn = redis.from_url(redis_url)
    with rq.Connection(conn):
        rq.Worker(['default']).work()
if __name__ == "__main__":
    main()
