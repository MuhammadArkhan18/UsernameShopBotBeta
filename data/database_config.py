import aiosqlite

class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_path = db_name

    async def init_db(self):
        sql_command = """
        CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255),
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS banned_users (
        user_id BIGINT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255),
        banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS banned_by_admins (
        admin_id BIGINT NOT NULL,
        admin_name VARCHAR(255) NOT NULL,
        admin_username VARCHAR(255),
        banned_user_id BIGINT PRIMARY KEY,
        banned_the_user_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_order_threads (
        user_id BIGINT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255),
        thread_id INT NOT NULL
        );
        """
        
        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")

            await db.executescript(sql_command)
            await db.commit()
            print("DB has been initialized with WAL mode")
    
    async def insert_data(self, table_name: str, primary_key: str, **kwargs):
        data = tuple(value for value in kwargs.values())
        sql_command = f"""
        INSERT INTO {table_name} ({', '.join(col for col in kwargs.keys())}) 
        VALUES ({', '.join(['?' for i in range(len(data))])}) 
        ON CONFLICT({primary_key}) 
        DO UPDATE SET {', '.join(f"{col} = EXCLUDED.{col}" for col in kwargs.keys() if col != primary_key)};
        """

        async with aiosqlite.connect(self.db_path, timeout=30.0) as db:
            await db.execute(sql_command, data)
            await db.commit()

    async def read_data_all(self, table_name: str, *args):
        sql_command = f"""
        SELECT {', '.join(col for col in args) if args != () else '*'} FROM {table_name};
        """
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(sql_command) as cursor:
                rows = await cursor.fetchall()
                return rows
    
    async def delete_data(self, table_name: str, primary_key: str, value_key):
        data = (value_key,)
        sql_command = f"""
        DELETE FROM {table_name} WHERE {primary_key} = ?;
        """

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(sql_command, data)
            await db.commit()
