# Chess Companion

An AI-powered chess companion that provides expert-level analysis and commentary for live chess games. Watch YouTube chess streams while getting real-time insights, historical context, and interactive analysis through natural voice conversation.

## What It Does

The Chess Companion transforms your chess viewing experience by combining:

- **Live Commentary**: Real-time position analysis with expert insights
- **Voice Interaction**: Ask questions about positions, moves, and strategies  
- **TV Control**: Search, play, and control YouTube chess content via voice
- **Historical Context**: Access to master games database for similar positions
- **Engine Analysis**: Stockfish evaluation with move suggestions and variations
- **Hypothetical Analysis**: "What if Magnus played Nf3 instead?" scenarios

## Key Features

### 🎯 Real-Time Position Recognition
- **2-second detection** from YouTube chess streams via Chromecast
- Specialized computer vision models for accurate board recognition
- Works across different chess broadcast formats and board styles

### 🧠 Expert-Level Analysis
- **Stockfish engine integration** for precise position evaluation
- **Historical precedent** from master games database
- **Strategic themes** and tactical pattern recognition
- **Both perspectives**: Pre-computed analysis for white and black

### 🎙️ Natural Voice Interaction
- **Gemini Live integration** for conversational chess analysis
- Ask questions like:
  - *"What should Magnus play here?"*
  - *"What happens if Nakamura takes that pawn?"*
  - *"Pause, let me think about this position"*
  - *"Show me similar games from the database"*

### 📺 Seamless TV Control
- **YouTube search and playback** via Chromecast control
- Voice commands: *"Play the Carlsen vs Nakamura semifinal"*
- **Pause/resume** for deeper analysis
- **Content memory** - remembers your viewing preferences

### 📚 Rich Historical Database
- **5,000+ chess-significant positions** from master games
- **Dual enhancement**: Human expert commentary + AI analysis
- **Vector similarity search** for finding related positions
- **Famous games collection** with annotated analysis

## Architecture Overview

```
YouTube Stream → Chromecast → HDMI Capture → Vision Pipeline → Chess Analysis
                                                     ↓
User Voice ← Gemini Live ← Analysis Engine ← Historical Database + Stockfish
```

### Core Components

- **Vision System**: Roboflow specialized models for chess board recognition
- **Analysis Engine**: Combines Stockfish + historical context + LLM synthesis  
- **Background Processing**: Three-tier system for real-time responsiveness
- **TV Controller**: ADB-based Chromecast control for content management
- **Vector Database**: Semantic search across chess positions and games

## Performance Highlights

- **19x speedup**: Position detection improved from 40s → 2s
- **Real-time capable**: Suitable for live game commentary
- **100% chess-significant**: Intelligent position filtering vs random sampling
- **Cost optimized**: $0.49 per 5,000 positions using efficient AI models
- **Production ready**: Robust error handling and graceful degradation

## Use Cases

### 🏆 Tournament Viewing
Watch live chess tournaments with expert commentary that includes:
- Time pressure analysis from broadcast context
- Player-specific insights and tendencies  
- Match stakes and tournament significance
- Historical head-to-head comparisons

### 📖 Educational Analysis
Learn from master games with:
- Strategic theme identification
- Tactical pattern recognition
- Alternative move exploration
- Historical precedent and context

### 🎮 Interactive Study
Engage with positions through:
- Hypothetical move analysis
- Engine evaluation explanations
- Similar position comparisons
- Opening and endgame insights

## Technical Requirements

### Hardware
- **HDMI capture device** for video input
- **Chromecast** or Android TV device
- **Computer** with sufficient processing power for real-time analysis

### Software Dependencies
- **Python 3.8+** with poetry for dependency management
- **Stockfish chess engine** for position analysis
- **Google AI services** (Gemini Live, Vision APIs)
- **Roboflow account** for specialized chess vision models
- **ADB (Android Debug Bridge)** for TV control

### Network Requirements
- **Stable internet** for AI service APIs
- **Local network access** to Chromecast device
- **YouTube access** for chess content streaming

## Getting Started

### 1. Hardware Setup
```bash
# Set up HDMI video loopback for capture
./chess/setup_hdmi_loopback.sh
```

### 2. Configuration
```bash
# Install dependencies
poetry install

# Configure API keys
export GOOGLE_API_KEY="your_gemini_api_key"
export ROBOFLOW_API_KEY="your_roboflow_api_key"
```

### 3. Database Setup
```bash
# Build chess positions database (optional - pre-built available)
poetry run python build_database.py input.pgn 5000 output.json
```

### 4. Launch Chess Companion
```bash
# Start with debug mode for development
poetry run python chess_companion_standalone.py --debug

# Production mode
poetry run python chess_companion_standalone.py
```

## Example Interactions

### Position Analysis
```
You: "What should Magnus play in this position?"
Companion: "Magnus, playing Black, should consider Nf6, developing the knight 
           while maintaining central control. The engine evaluates this at -0.3, 
           slightly favoring Black. This position is similar to Game 4 from the 
           2021 World Championship where Magnus used similar piece coordination..."
```

### Hypothetical Scenarios  
```
You: "What happens if he takes the pawn with the rook?"
Companion: "If Rxe5, the position changes from +0.2 to -0.8 after dxe5, 
           opening the d-file for White's rook. This tactical shot improves 
           White's position significantly, similar to the breakthrough 
           Carlsen achieved against Nepo in their rapid match..."
```

### Content Control
```
You: "Can you play the Hikaru vs Magnus game from yesterday?"
Companion: "🎬 Bringing up 'Hikaru vs Magnus'... 
           [Searches YouTube and starts playback]
           This looks like their Speed Chess Championship match. 
           Should I analyze the current position?"
```

## Advanced Features

### 🔍 Historical Context Integration
- **Master games database** with expert annotations
- **Vector similarity search** for position comparisons  
- **Opening preparation** and novelty detection
- **Endgame tablebase** integration for perfect play

### 🎯 Broadcast Context Awareness
- **Player identification** from video streams
- **Time pressure analysis** from clock displays
- **Match significance** and tournament context
- **Biometric data** integration when available

### 🚀 Performance Optimizations
- **Background processing** for instant responses
- **Cached analysis** for frequently seen positions
- **Parallel computation** for both player perspectives
- **Scene detection** for efficient resource usage

## Development Status

### ✅ Production Ready
- Real-time position recognition (2s latency)
- Voice interaction with Gemini Live
- TV control and content management
- Expert-level chess analysis pipeline
- Historical database with 5,000+ positions

### 🔄 Active Development
- Database expansion with more master games
- Multi-stream support for tournament coverage
- Mobile integration for portable analysis
- Educational features for chess improvement

### 🎯 Future Roadmap
- Opening preparation tools
- Player style analysis
- Tournament preparation features
- Integration with chess platforms (Chess.com, Lichess)

## Contributing

The Chess Companion is built on proven architectural patterns and welcomes contributions in:

- **Vision model optimization** for different board styles
- **Database expansion** with annotated master games  
- **Analysis enhancement** with specialized chess knowledge
- **User experience improvements** for natural interaction

## Architecture Insights

### Key Technical Breakthroughs
1. **Specialized beats general**: Chess-specific vision models outperform general AI
2. **Speed enables architecture**: 19x performance improvement enabled new system design
3. **Quality data over quantity**: Chess-significant positions better than random sampling
4. **Parallel analysis**: Computing both perspectives avoids brittle turn detection
5. **Background processing**: Pre-computation provides responsive user experience

### Performance Philosophy
- **Real-time capability** prioritized over perfect accuracy
- **User experience** drives technical architecture decisions  
- **Graceful degradation** ensures system reliability
- **Cost efficiency** balanced with analysis quality

---

*The Chess Companion represents a sophisticated evolution of AI-powered chess analysis, combining the precision of engine evaluation with the insight of human expertise and the convenience of natural voice interaction.*
