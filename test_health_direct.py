#!/usr/bin/env python3
"""Quick test to call health_check directly"""
import asyncio
import sys

async def test_health():
    # Import the protocol
    sys.path.insert(0, '.')
    
    try:
        from core.protocols.UBEC_protocol import UBECProtocol
        print("✓ Imported UBECProtocol")
        
        # Try to create minimal instance
        from core.db.database_manager import AsyncDatabaseManager
        from stellar_sdk import ServerAsync
        
        db = AsyncDatabaseManager(
            host='localhost',
            database='ubec',
            user='ubec_app',
            schema='ubec_main'
        )
        await db.initialize()
        
        stellar = ServerAsync('https://horizon-testnet.stellar.org')
        
        config = {
            'asset_code': 'UBEC',
            'issuer': 'GXXXXXXXXX',
            'element': 'air'
        }
        
        protocol = UBECProtocol(db, config, stellar)
        await protocol.initialize()
        
        print("✓ Created and initialized protocol")
        
        # Try health check
        health = await protocol.health_check()
        print(f"✓ Health check result: {health}")
        
        await db.close()
        await stellar.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_health())
