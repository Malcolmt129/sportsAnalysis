import unittest
import dbmanagement as dbm






class TestDBfunctions(unittest.TestCase):



    def test_db_initiation(self):
        with dbm.get_db_connection() as conn:
            tables = conn.execute(""" SELECT name FROM  sqlite_master WHERE type='table'; """)
            
            tablesNames = [row[0] for row in tables.fetchall()] 
            
            self.assertEqual(len(tablesNames), 4) 
    

    
