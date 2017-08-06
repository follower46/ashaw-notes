import redis
import configparser

__iloveglobals__ = None

def get_redis_connection():
    global __iloveglobals__

    config = configparser.ConfigParser()
    config.read('notes.config')

    if not __iloveglobals__:
        __iloveglobals__ = redis.StrictRedis(
            host=config.get('redis_server', 'endpoint'), 
            port=config.get('redis_server', 'port'), 
            db=config.get('redis_server', 'db'),
            password=config.get('redis_server', 'password')
        )

    return __iloveglobals__