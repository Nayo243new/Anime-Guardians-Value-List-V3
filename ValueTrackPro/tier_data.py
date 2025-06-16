import pandas as pd

class TierListManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_tier_data(self):
        """Get all tier list data"""
        return self.db.execute_query("""
            SELECT name, tier, value, demand, trend, information
            FROM characters
            ORDER BY 
                CASE tier
                    WHEN 'S+' THEN 1
                    WHEN 'S' THEN 2
                    WHEN 'A+' THEN 3
                    WHEN 'A' THEN 4
                    WHEN 'A-' THEN 5
                    ELSE 6
                END,
                value DESC
        """)
    
    def get_character_value(self, character_name):
        """Get current value of a character"""
        result = self.db.execute_query("""
            SELECT value FROM characters WHERE name = %s
        """, (character_name,))
        
        if not result.empty:
            return result.iloc[0]['value']
        return 0
    
    def get_character_data(self, character_name):
        """Get complete character data"""
        return self.db.execute_query("""
            SELECT * FROM characters WHERE name = %s
        """, (character_name,))
    
    def update_character(self, name, value, demand, tier, trend, information):
        """Update character data (Admin only)"""
        return self.db.execute_query("""
            UPDATE characters 
            SET value = %s, demand = %s, tier = %s, trend = %s, information = %s, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s
        """, (value, demand, tier, trend, information, name), fetch=False)
    
    def add_character(self, name, value, demand, tier, trend, information):
        """Add new character (Admin only)"""
        # Check if character already exists
        existing = self.db.execute_query("""
            SELECT name FROM characters WHERE name = %s
        """, (name,))
        
        if not existing.empty:
            return False
        
        return self.db.execute_query("""
            INSERT INTO characters (name, value, demand, tier, trend, information)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, value, demand, tier, trend, information), fetch=False)
    
    def delete_character(self, name):
        """Delete character (Admin only)"""
        return self.db.execute_query("""
            DELETE FROM characters WHERE name = %s
        """, (name,), fetch=False)
    
    def search_characters(self, query):
        """Search characters by name"""
        return self.db.execute_query("""
            SELECT name, tier, value, demand, trend, information
            FROM characters
            WHERE name ILIKE %s
            ORDER BY value DESC
        """, (f"%{query}%",))
    
    def get_characters_by_tier(self, tier):
        """Get characters by tier"""
        return self.db.execute_query("""
            SELECT name, tier, value, demand, trend, information
            FROM characters
            WHERE tier = %s
            ORDER BY value DESC
        """, (tier,))
    
    def get_trending_characters(self):
        """Get trending characters"""
        return self.db.execute_query("""
            SELECT name, tier, value, demand, trend, information
            FROM characters
            WHERE trend = 'Overpriced' OR demand >= 8
            ORDER BY demand DESC, value DESC
            LIMIT 10
        """)
    
    def get_tier_statistics(self):
        """Get statistics by tier"""
        return self.db.execute_query("""
            SELECT 
                tier,
                COUNT(*) as character_count,
                AVG(value) as avg_value,
                AVG(demand) as avg_demand
            FROM characters
            GROUP BY tier
            ORDER BY 
                CASE tier
                    WHEN 'S+' THEN 1
                    WHEN 'S' THEN 2
                    WHEN 'A+' THEN 3
                    WHEN 'A' THEN 4
                    WHEN 'A-' THEN 5
                    ELSE 6
                END
        """)
