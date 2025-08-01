import aiosqlite
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class RiskDatabase:
    def __init__(self, db_path: str = "risk_data.db"):
        self.db_path = db_path
        logger.info(f"Initializing RiskDatabase at {db_path}")
    
    async def initialize(self):
        """Initialize database with tables and seed data"""
        logger.info("Creating database tables and seeding initial data")
        
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            await self._create_tables(db)
            
            # Seed with realistic historical data
            await self._seed_initial_data(db)
            
            await db.commit()
            
        logger.info("Database initialization completed")
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create all database tables"""
        
        # Historical delivery performance by carrier and zip
        await db.execute("""
            CREATE TABLE IF NOT EXISTS delivery_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carrier TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                total_deliveries INTEGER DEFAULT 0,
                delayed_deliveries INTEGER DEFAULT 0,
                total_delay_hours REAL DEFAULT 0,
                avg_delay_hours REAL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(carrier, zip_code)
            )
        """)
        
        # Geographic risk factors
        await db.execute("""
            CREATE TABLE IF NOT EXISTS geographic_risk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT UNIQUE NOT NULL,
                city TEXT,
                state TEXT,
                region TEXT,
                urban_rural TEXT,  -- 'urban', 'suburban', 'rural'
                base_risk_score INTEGER DEFAULT 0,
                weather_risk_multiplier REAL DEFAULT 1.0,
                traffic_complexity INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Carrier performance metrics
        await db.execute("""
            CREATE TABLE IF NOT EXISTS carrier_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carrier TEXT UNIQUE NOT NULL,
                total_deliveries INTEGER DEFAULT 0,
                on_time_deliveries INTEGER DEFAULT 0,
                delayed_deliveries INTEGER DEFAULT 0,
                average_delay_hours REAL DEFAULT 0,
                reliability_score INTEGER DEFAULT 50,  -- 0-100 scale
                peak_season_performance_drop INTEGER DEFAULT 0,  -- additional risk during holidays
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Time-based risk patterns
        await db.execute("""
            CREATE TABLE IF NOT EXISTS temporal_risk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,  -- 'day_of_week', 'month', 'holiday_period'
                pattern_value TEXT NOT NULL,  -- 'monday', 'december', 'christmas_week'
                risk_multiplier REAL DEFAULT 1.0,
                description TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pattern_type, pattern_value)
            )
        """)
        
        # Route-specific performance
        await db.execute("""
            CREATE TABLE IF NOT EXISTS route_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin_zip TEXT,
                destination_zip TEXT,
                carrier TEXT,
                distance_miles INTEGER,
                typical_transit_days INTEGER,
                success_rate REAL DEFAULT 1.0,  -- 0.0 to 1.0
                avg_delay_hours REAL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(origin_zip, destination_zip, carrier)
            )
        """)
        
        # Actual delivery outcomes (for learning)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS delivery_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id TEXT NOT NULL,
                carrier TEXT NOT NULL,
                origin_zip TEXT,
                destination_zip TEXT,
                scheduled_date DATE,
                actual_delivery_date DATE,
                was_delayed BOOLEAN DEFAULT FALSE,
                delay_hours REAL DEFAULT 0,
                delay_reasons TEXT,  -- JSON array of reasons
                weather_conditions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Customer actions tracking
        await db.execute("""
            CREATE TABLE IF NOT EXISTS customer_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id TEXT NOT NULL,
                action TEXT NOT NULL,  -- 'Accept Delay', 'Request Refund', 'Resend'
                customer_id TEXT,
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                processing_notes TEXT
            )
        """)
        
        logger.info("All database tables created successfully")
    
    async def _seed_initial_data(self, db: aiosqlite.Connection):
        """Seed database with realistic historical performance data"""
        logger.info("Seeding database with initial historical data")
        
        # Seed carrier performance based on industry averages
        carrier_data = [
            ("UPS", 1000000, 920000, 80000, 6.2, 85, 15),
            ("FedEx", 800000, 760000, 40000, 4.8, 88, 12),
            ("USPS", 1200000, 1020000, 180000, 8.1, 78, 25),
            ("DHL", 300000, 276000, 24000, 5.5, 82, 18),
        ]
        
        for carrier, total, on_time, delayed, avg_delay, reliability, peak_drop in carrier_data:
            await db.execute("""
                INSERT OR REPLACE INTO carrier_performance 
                (carrier, total_deliveries, on_time_deliveries, delayed_deliveries, 
                 average_delay_hours, reliability_score, peak_season_performance_drop)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (carrier, total, on_time, delayed, avg_delay, reliability, peak_drop))
        
        # Seed geographic risk for our mock cities
        geo_data = [
            ("98101", "Seattle", "WA", "Pacific Northwest", "urban", 15, 1.3, 25),
            ("10001", "New York", "NY", "Northeast", "urban", 20, 1.1, 35),
            ("90210", "Beverly Hills", "CA", "West Coast", "suburban", 8, 0.9, 15),
            ("33101", "Miami", "FL", "Southeast", "urban", 25, 1.5, 20),
            ("60601", "Chicago", "IL", "Midwest", "urban", 18, 1.2, 30),
        ]
        
        for zip_code, city, state, region, urban_rural, base_risk, weather_mult, traffic in geo_data:
            await db.execute("""
                INSERT OR REPLACE INTO geographic_risk 
                (zip_code, city, state, region, urban_rural, base_risk_score, 
                 weather_risk_multiplier, traffic_complexity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (zip_code, city, state, region, urban_rural, base_risk, weather_mult, traffic))
        
        # Seed temporal risk patterns
        temporal_data = [
            ("day_of_week", "monday", 1.1, "Monday packages often delayed due to weekend backlog"),
            ("day_of_week", "friday", 1.05, "End of week rush"),
            ("month", "december", 1.4, "Holiday season rush"),
            ("month", "november", 1.2, "Black Friday and Thanksgiving impact"),
            ("holiday_period", "christmas_week", 1.6, "Week of Christmas"),
            ("holiday_period", "thanksgiving_week", 1.3, "Thanksgiving week"),
        ]
        
        for pattern_type, pattern_value, multiplier, description in temporal_data:
            await db.execute("""
                INSERT OR REPLACE INTO temporal_risk 
                (pattern_type, pattern_value, risk_multiplier, description)
                VALUES (?, ?, ?, ?)
            """, (pattern_type, pattern_value, multiplier, description))
        
        # Seed some historical delivery performance by carrier/zip combinations
        performance_data = []
        import random
        
        carriers = ["UPS", "FedEx", "USPS", "DHL"]
        zip_codes = ["98101", "10001", "90210", "33101", "60601"]
        
        for carrier in carriers:
            for zip_code in zip_codes:
                total_deliveries = random.randint(1000, 5000)
                delay_rate = random.uniform(0.05, 0.25)  # 5-25% delay rate
                delayed = int(total_deliveries * delay_rate)
                avg_delay = random.uniform(3.0, 12.0)
                
                performance_data.append((carrier, zip_code, total_deliveries, delayed, avg_delay))
        
        for carrier, zip_code, total, delayed, avg_delay in performance_data:
            await db.execute("""
                INSERT OR REPLACE INTO delivery_performance 
                (carrier, zip_code, total_deliveries, delayed_deliveries, avg_delay_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (carrier, zip_code, total, delayed, avg_delay))
        
        logger.info(f"Seeded database with {len(carrier_data)} carriers, {len(geo_data)} geographic areas, and {len(performance_data)} performance records")
    
    async def get_carrier_risk(self, carrier: str) -> int:
        """Get risk score for a carrier based on historical performance"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT reliability_score, peak_season_performance_drop, average_delay_hours
                FROM carrier_performance 
                WHERE carrier = ?
            """, (carrier,))
            
            result = await cursor.fetchone()
            if result:
                reliability, peak_drop, avg_delay = result
                # Convert reliability (higher is better) to risk (lower is better)
                base_risk = 100 - reliability
                
                # Add seasonal adjustment if we're in peak season
                current_month = datetime.now().month
                if current_month in [11, 12]:  # Holiday season
                    base_risk += peak_drop
                
                logger.debug(f"Carrier {carrier} risk: base={base_risk}, reliability={reliability}")
                return min(base_risk, 50)  # Cap at 50 points
            else:
                logger.warning(f"No performance data found for carrier {carrier}, using default risk")
                return 25  # Default risk for unknown carriers
    
    async def get_geographic_risk(self, zip_code: str) -> int:
        """Get risk score for a geographic area"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT base_risk_score, traffic_complexity, weather_risk_multiplier
                FROM geographic_risk 
                WHERE zip_code = ?
            """, (zip_code,))
            
            result = await cursor.fetchone()
            if result:
                base_risk, traffic, weather_mult = result
                total_risk = base_risk + (traffic * 0.3)  # Traffic adds up to 10 points
                
                logger.debug(f"Geographic risk for {zip_code}: base={base_risk}, traffic={traffic}, total={total_risk}")
                return int(min(total_risk, 30))  # Cap at 30 points
            else:
                logger.warning(f"No geographic data for zip {zip_code}, using default risk")
                return 10  # Default risk for unknown areas
    
    async def get_delivery_performance_risk(self, carrier: str, zip_code: str) -> int:
        """Get specific carrier-zip combination risk based on historical data"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT total_deliveries, delayed_deliveries, avg_delay_hours
                FROM delivery_performance 
                WHERE carrier = ? AND zip_code = ?
            """, (carrier, zip_code))
            
            result = await cursor.fetchone()
            if result:
                total, delayed, avg_delay = result
                if total > 0:
                    delay_rate = delayed / total
                    # Convert delay rate to risk score (0-20 points)
                    risk_score = int(delay_rate * 100)  # 10% delay rate = 10 points
                    
                    # Add delay severity factor
                    if avg_delay > 8:  # More than 8 hours average delay
                        risk_score += 5
                    
                    logger.debug(f"Performance risk for {carrier} to {zip_code}: delay_rate={delay_rate:.2%}, avg_delay={avg_delay}h, risk={risk_score}")
                    return min(risk_score, 20)  # Cap at 20 points
            
            return 0  # No specific performance penalty if no data
    
    async def get_temporal_risk(self, delivery_date: str) -> Tuple[int, List[str]]:
        """Get time-based risk factors"""
        try:
            date_obj = datetime.strptime(delivery_date, "%Y-%m-%d")
        except ValueError:
            return 0, []
        
        risk_score = 0
        reasons = []
        
        async with aiosqlite.connect(self.db_path) as db:
            # Check day of week
            day_name = date_obj.strftime("%A").lower()
            cursor = await db.execute("""
                SELECT risk_multiplier, description
                FROM temporal_risk 
                WHERE pattern_type = 'day_of_week' AND pattern_value = ?
            """, (day_name,))
            
            day_result = await cursor.fetchone()
            if day_result:
                multiplier, description = day_result
                if multiplier > 1.0:
                    additional_risk = int((multiplier - 1.0) * 20)  # Convert multiplier to points
                    risk_score += additional_risk
                    reasons.append(description)
            
            # Check month
            month_name = date_obj.strftime("%B").lower()
            cursor = await db.execute("""
                SELECT risk_multiplier, description
                FROM temporal_risk 
                WHERE pattern_type = 'month' AND pattern_value = ?
            """, (month_name,))
            
            month_result = await cursor.fetchone()
            if month_result:
                multiplier, description = month_result
                if multiplier > 1.0:
                    additional_risk = int((multiplier - 1.0) * 25)  # Seasonal impact is higher
                    risk_score += additional_risk
                    reasons.append(description)
        
        logger.debug(f"Temporal risk for {delivery_date}: {risk_score} points, reasons: {reasons}")
        return min(risk_score, 25), reasons
    
    async def record_delivery_outcome(self, package_id: str, carrier: str, 
                                    origin_zip: str, destination_zip: str,
                                    scheduled_date: str, actual_date: str,
                                    delay_reasons: List[str] = None):
        """Record actual delivery outcome for learning"""
        logger.info(f"Recording delivery outcome for package {package_id}")
        
        try:
            scheduled = datetime.strptime(scheduled_date, "%Y-%m-%d")
            actual = datetime.strptime(actual_date, "%Y-%m-%d")
            
            delay_hours = (actual - scheduled).total_seconds() / 3600
            was_delayed = delay_hours > 24  # More than 1 day late
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO delivery_outcomes 
                    (package_id, carrier, origin_zip, destination_zip, scheduled_date, 
                     actual_delivery_date, was_delayed, delay_hours, delay_reasons)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (package_id, carrier, origin_zip, destination_zip, scheduled_date,
                      actual_date, was_delayed, delay_hours, json.dumps(delay_reasons or [])))
                
                await db.commit()
                
                # Update aggregated performance data
                await self._update_performance_metrics(db, carrier, destination_zip, 
                                                     was_delayed, delay_hours)
            
            logger.info(f"Recorded outcome: delayed={was_delayed}, delay_hours={delay_hours:.1f}")
            
        except Exception as e:
            logger.error(f"Error recording delivery outcome: {e}")
    
    async def _update_performance_metrics(self, db: aiosqlite.Connection, 
                                        carrier: str, zip_code: str, 
                                        was_delayed: bool, delay_hours: float):
        """Update aggregated performance metrics based on new outcome"""
        
        # Update delivery_performance table
        await db.execute("""
            INSERT INTO delivery_performance (carrier, zip_code, total_deliveries, delayed_deliveries, total_delay_hours)
            VALUES (?, ?, 1, ?, ?)
            ON CONFLICT(carrier, zip_code) DO UPDATE SET
                total_deliveries = total_deliveries + 1,
                delayed_deliveries = delayed_deliveries + ?,
                total_delay_hours = total_delay_hours + ?,
                avg_delay_hours = total_delay_hours / total_deliveries,
                last_updated = CURRENT_TIMESTAMP
        """, (carrier, zip_code, 1 if was_delayed else 0, delay_hours,
              1 if was_delayed else 0, delay_hours))
        
        await db.commit()
    
    async def record_customer_action(self, package_id: str, action: str, 
                                   customer_id: str = None, notes: str = None) -> Dict:
        """Record customer action in database"""
        logger.info(f"Recording customer action: {action} for package {package_id}")
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO customer_actions (package_id, action, customer_id, notes)
                VALUES (?, ?, ?, ?)
            """, (package_id, action, customer_id, notes))
            
            action_id = cursor.lastrowid
            await db.commit()
            
            logger.info(f"Customer action recorded with ID: {action_id}")
            
            return {
                "id": action_id,
                "package_id": package_id,
                "action": action,
                "customer_id": customer_id,
                "notes": notes,
                "timestamp": datetime.now().isoformat(),
                "processed": False
            }
    
    async def get_customer_actions(self, limit: int = 50) -> List[Dict]:
        """Get recent customer actions"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, package_id, action, customer_id, notes, timestamp, processed, processing_notes
                FROM customer_actions 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            actions = await cursor.fetchall()
            
            return [
                {
                    "id": action[0],
                    "package_id": action[1],
                    "action": action[2],
                    "customer_id": action[3],
                    "notes": action[4],
                    "timestamp": action[5],
                    "processed": bool(action[6]),
                    "processing_notes": action[7]
                }
                for action in actions
            ]
    
    async def get_customer_action_stats(self) -> Dict:
        """Get customer action statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get action counts by type
            cursor = await db.execute("""
                SELECT action, COUNT(*) as count
                FROM customer_actions
                GROUP BY action
                ORDER BY count DESC
            """)
            action_counts = await cursor.fetchall()
            
            # Get recent activity (last 7 days)
            cursor = await db.execute("""
                SELECT COUNT(*) as total_actions
                FROM customer_actions
                WHERE timestamp > datetime('now', '-7 days')
            """)
            recent_activity = await cursor.fetchone()
            
            # Get processing status
            cursor = await db.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN processed THEN 1 ELSE 0 END) as processed,
                    SUM(CASE WHEN NOT processed THEN 1 ELSE 0 END) as pending
                FROM customer_actions
            """)
            processing_stats = await cursor.fetchone()
            
            return {
                "action_breakdown": [{"action": ac[0], "count": ac[1]} for ac in action_counts],
                "recent_activity": recent_activity[0] if recent_activity else 0,
                "processing_stats": {
                    "total": processing_stats[0] if processing_stats else 0,
                    "processed": processing_stats[1] if processing_stats else 0,
                    "pending": processing_stats[2] if processing_stats else 0
                }
            }

    async def get_performance_stats(self) -> Dict:
        """Get overall performance statistics for dashboard"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get carrier stats
            cursor = await db.execute("""
                SELECT carrier, total_deliveries, on_time_deliveries, reliability_score
                FROM carrier_performance 
                ORDER BY reliability_score DESC
            """)
            carriers = await cursor.fetchall()
            
            # Get geographic stats
            cursor = await db.execute("""
                SELECT zip_code, city, base_risk_score, traffic_complexity
                FROM geographic_risk 
                ORDER BY base_risk_score DESC
            """)
            locations = await cursor.fetchall()
            
            # Get recent outcomes
            cursor = await db.execute("""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN was_delayed THEN 1 ELSE 0 END) as delayed,
                       AVG(delay_hours) as avg_delay
                FROM delivery_outcomes 
                WHERE created_at > datetime('now', '-30 days')
            """)
            recent_stats = await cursor.fetchone()
            
            # Get customer action stats
            customer_stats = await self.get_customer_action_stats()
            
            return {
                "carriers": [{"carrier": c[0], "deliveries": c[1], "on_time": c[2], "reliability": c[3]} 
                           for c in carriers],
                "locations": [{"zip": l[0], "city": l[1], "risk": l[2], "traffic": l[3]} 
                            for l in locations],
                "recent_performance": {
                    "total_deliveries": recent_stats[0] or 0,
                    "delayed_deliveries": recent_stats[1] or 0,
                    "average_delay_hours": recent_stats[2] or 0
                } if recent_stats else {},
                "customer_actions": customer_stats
            }


# Global database instance
risk_db = RiskDatabase()