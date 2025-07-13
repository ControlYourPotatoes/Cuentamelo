import asyncio
import asyncpg

async def create_tables():
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/cuentamelo")

    # Create basic tables for characters and conversations
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            personality_type VARCHAR(50) NOT NULL,
            language VARCHAR(10) DEFAULT 'es-pr',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    await conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            character_id INTEGER REFERENCES characters(id),
            tweet_id VARCHAR(50),
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add some additional tables for the full system
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS news_items (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            content TEXT,
            source_url VARCHAR(500),
            published_at TIMESTAMP,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            keywords TEXT[],
            relevance_score FLOAT DEFAULT 0.0
        )
    ''')

    await conn.execute('''
        CREATE TABLE IF NOT EXISTS character_responses (
            id SERIAL PRIMARY KEY,
            character_id INTEGER REFERENCES characters(id),
            news_item_id INTEGER REFERENCES news_items(id),
            response_text TEXT NOT NULL,
            tweet_id VARCHAR(50),
            engagement_score FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    await conn.close()
    print("✅ Database tables created successfully")

async def insert_sample_characters():
    """Insert the four Puerto Rican AI characters"""
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/cuentamelo")
    
    characters = [
        ("Jovani Vázquez", "influencer", "es-pr"),
        ("Político Boricua", "political_figure", "es-pr"),
        ("Ciudadano Boricua", "citizen", "es-pr"),
        ("Historiador Cultural", "cultural_historian", "es-pr")
    ]
    
    for name, personality_type, language in characters:
        await conn.execute('''
            INSERT INTO characters (name, personality_type, language)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
        ''', name, personality_type, language)
    
    await conn.close()
    print("✅ Sample characters inserted")

if __name__ == "__main__":
    print("🗃️ Setting up database tables...")
    asyncio.run(create_tables())
    asyncio.run(insert_sample_characters())
    print("🎉 Database setup complete!") 