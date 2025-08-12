import queue
import threading
from typing import Optional
import chess.engine


class StockfishEnginePool:
    def __init__(self, pool_size: int = 4, threads_per_engine: int = 1, purpose: str = "analysis"):
        self.pool_size = pool_size
        self.threads_per_engine = threads_per_engine
        self.purpose = purpose
        self.engines = queue.Queue()
        self.lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Pre-create Stockfish engines"""
        print(f"   Initializing Stockfish pool for {self.purpose} ({self.pool_size} engines)...")
        
        for i in range(self.pool_size):
            try:
                engine = chess.engine.SimpleEngine.popen_uci("stockfish")
                # Configure engine
                try:
                    engine.configure({"Threads": self.threads_per_engine})
                except Exception as config_error:
                    print(f"   ⚠️ Engine {i+1} config failed: {config_error}")
                    print(f"   ⚠️ Using Stockfish defaults...")
                
                self.engines.put(engine)
                print(f"   Engine {i+1}/{self.pool_size} ready")
                
            except Exception as e:
                print(f"   ❌ Failed to create engine {i+1}: {e}")
                break
    
    def get_engine(self) -> chess.engine.SimpleEngine:
        """Get an engine from pool (blocks until available)"""
        return self.engines.get()
    
    def return_engine(self, engine: chess.engine.SimpleEngine):
        """Return engine to pool"""
        self.engines.put(engine)
    
    def cleanup(self):
        """Shut down all engines"""
        while not self.engines.empty():
            try:
                engine = self.engines.get_nowait()
                engine.quit()
            except queue.Empty:
                break


# Factory functions for common use cases
def create_quick_analysis_pool(pool_size: int = 4) -> StockfishEnginePool:
    """Pool for quick position filtering"""
    return StockfishEnginePool(pool_size, threads_per_engine=1, purpose="quick analysis")


def create_deep_analysis_pool(pool_size: int = 4) -> StockfishEnginePool:
    """Pool for deep position analysis"""
    return StockfishEnginePool(pool_size, threads_per_engine=2, purpose="deep analysis")


# Async wrapper functions for live companion integration
import asyncio

async def analyze_position_async(engine_pool: StockfishEnginePool, fen: str, time_limit: float = 0.5) -> dict:
    """Async wrapper for position analysis using engine pool"""
    try:
        engine = engine_pool.get_engine()
        
        def _analyze():
            import chess
            import chess.engine
            board = chess.Board(fen)
            info = engine.analyse(board, chess.engine.Limit(time=time_limit))
            return info
        
        # Run analysis in thread pool
        info = await asyncio.to_thread(_analyze)
        
        engine_pool.return_engine(engine)
        
        return {
            "evaluation": info.get("score").relative.cp if info.get("score") else 0,
            "best_move": str(info.get("pv", [None])[0]) if info.get("pv") else None,
            "depth": info.get("depth", 0),
            "nodes": info.get("nodes", 0)
        }
        
    except Exception as e:
        print(f"❌ Async engine analysis failed: {e}")
        return {"evaluation": 0, "best_move": None, "depth": 0, "nodes": 0}
