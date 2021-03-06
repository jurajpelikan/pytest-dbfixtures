.. _howtouse:


How to use
==========

Mongo
-----

.. sourcecode:: python

    def test_using_mongo(mongodb):
        db = mongodb['test_database']
        db.test.insert({'woof': 'woof'})
        documents = db.test.find_one()


    from pytest_dbfixtures import factories
    mongo_proc2 = factories.mongo_proc(port=27070, params='--nojournal --noauth --nohttpinterface --noprealloc')
    mongodb2 = factories.mongodb('mongo_proc2')

    def test_second_mongo(mongodb, mongodb2):
        test_data_one = {
            "test1": "test1",
        }
        db = mongodb['test_db']
        db.test.insert(test_data_one)
        assert db.test.find_one()['test1'] == 'test1'

        test_data_two = {
            "test2": "test2",
        }
        db = mongodb2['test_db']
        db.test.insert(test_data_two)
        assert db.test.find_one()['test2'] == 'test2'

MySQL
-----

.. sourcecode:: python

    def test_using_mysql(mysql):
        mysql.query("SELECT CURRENT_USER()")


    # second database
    from pytest_dbfixtures import factories

    query = '''CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20),
    species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);'''

    mysql_proc2 = factories.mysql_proc(port=3308, params='--skip-sync-frm')
    mysql2 = factories.mysql('mysql_proc2')

    def test_mysql_newfixture(mysql, mysql2):
        cursor = mysql.cursor()
        cursor.execute(query)
        mysql.commit()
        cursor.close()

        cursor = mysql2.cursor()
        cursor.execute(query)
        mysql2.commit()
        cursor.close()


RabbitMQ
--------

.. sourcecode:: python

    def test_using_rabbit(rabbitmq):
        channel = rabbitmq.channel()

Redis
-----

.. sourcecode:: python

    def test_using_redis(redisdb):
        redisdb.set('woof', 'woof')
        woof = redisdb.get('woof')

    from pytest_dbfixtures import factories

    redis_proc2 = factories.redis_proc(port=6381)
    redisdb2 = factories.redisdb('redis_proc2')

    def test_using_two_redis(redisdb, redisdb2):
        redisdb.set('woof1', 'woof1')
        redisdb2.set('woof2', 'woof12')

        woof1 = redisdb.get('woof1')
        woof2 = redisdb2.get('woof2')


Random process port
-------------------

Instead of specifing precise port that process will be bound to you can pass '?' in port argument or specify port range e.g. '2000-3000' or comma-separated list or ranges e.g. '2000-3000,4000-4500,5000'. Library will randomly choose a port that is not used by any other application.

.. sourcecode:: python

    from pytest_dbfixtures import factories

    redis_rand_proc = factories.redis_proc(port='?')
    redisdb_rand = factories.redisdb('redis_rand_proc')

    def test_using_random_ports(redisdb_rand, redisdb):
        print redisdb_rand.port  # will print randomly selected redis port
        print redisdb.port  # will print default redis port
