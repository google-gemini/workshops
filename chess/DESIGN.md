# Chess Companion System Design

## Overview

The Chess Companion is an AI-powered system that provides expert-level chess analysis and commentary for live chess games. It combines real-time computer vision, chess engine analysis, historical game databases, and conversational AI to deliver sophisticated chess insights through natural voice interaction.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Video Input   │    │   Audio Input    │    │  User Voice     │
│  (HDMI/YouTube) │    │ (Commentary/TV)  │    │   Commands      │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Chess Companion Core                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Vision    │  │    Audio    │  │    Analysis Engine      │ │
│  │  Pipeline   │  │ Processing  │  │                         │ │
│  │             │  │             │  │ • Stockfish Engine      │ │
│  │ • Scene Det │  │ • Speech    │  │ • Vector Database       │ │
│  │ • FEN Det   │  │   Transcr   │  │ • LLM Enhancement       │ │
│  │ • Board Seg │  │ • Commentary│  │ • Historical Context    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Gemini Live Integration                     │
│              (Conversational AI + Tool Orchestration)          │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────┐
│   Audio Output  │
│  (Commentary)   │
└─────────────────┘
```

### Core Components

#### 1. Vision Pipeline
**Purpose**: Real-time chess position recognition from video streams
**Performance**: 2-second FEN detection (19x speedup from 40s baseline)

**Architecture**:
```
Video Capture → Scene Detection → Board Segmentation → Piece Detection → FEN Generation
     ↓              ↓                    ↓                   ↓              ↓
  1920x1080    Layout Changes      Roboflow API        Direct FEN      Chess Position
   30fps       (10-30s intervals)   (~1.6s)           Symbols (~464ms)    (~1ms)
```

**Key Technologies**:
- **HDMI Capture**: v4l2loopback for device multiplexing
- **Scene Detection**: PySceneDetect with HistogramDetector
- **Board Segmentation**: Roboflow `chessboard-segmentation/1`
- **Piece Detection**: Roboflow `chess-piece-detection-lnpzs/1`

#### 2. Analysis Engine
**Purpose**: Multi-source chess analysis combining engine evaluation, historical context, and strategic insights

**Components**:
- **Stockfish Integration**: Position evaluation and move suggestions
- **Vector Database**: 5,000+ chess-significant positions with embeddings
- **LLM Enhancement**: Gemini 2.0 Flash-Lite for strategic descriptions
- **Historical Context**: Master games database with expert annotations

**Analysis Flow**:
```
Current Position → Parallel Analysis → Cached Results
       ↓               ↓        ↓           ↓
   FEN String    White Analysis  Black    Instant
                      ↓         Analysis   Response
              Stockfish + Vector + LLM
```

#### 3. Background Processing Architecture
**Design Principle**: Pre-compute expensive analysis during idle time for instant user responses

**Three-Tier System**:
1. **Scene Detection** (10-30s intervals): Camera angle changes, board layout updates
2. **FEN Detection** (3-5s intervals): Chess position monitoring with cached board masks
3. **Position Analysis** (on change): Pre-compute both white/black perspectives

#### 4. Conversational Interface
**Technology**: Gemini Live with custom tool integration
**Interaction Model**: Natural voice commands with contextual understanding

**Tool Architecture**:
- `analyze_current_position`: Comprehensive position analysis
- `analyze_hypothetical_move`: "What if" scenario analysis
- `search_related_games`: Historical precedent from vector database
- `play_content`: TV control for chess content
- `pause_playback`: Media control with UI cleanup

## Key Design Decisions

### 1. Specialized vs General AI Models
**Decision**: Use chess-specific computer vision models over general multimodal LLMs
**Rationale**: 19x performance improvement with maintained accuracy
**Trade-off**: Model dependency vs speed and reliability

### 2. Parallel Analysis Strategy
**Decision**: Pre-compute analysis for both white and black perspectives
**Rationale**: Sidesteps brittle turn detection, enables instant responses
**Trade-off**: 2x computational cost for significantly better reliability

### 3. Chess-Significance Filtering
**Decision**: Intelligent position selection based on evaluation swings and tactical moments
**Rationale**: 100% chess-significant positions vs ~20% with arbitrary sampling
**Implementation**: Stockfish evaluation analysis for position importance

### 4. Background Processing Architecture
**Decision**: Three-tier background processing with cached results
**Rationale**: Shift expensive computation to idle time for responsive UX
**Benefit**: Sub-second response times for cached positions

### 5. Vector Database Design
**Decision**: Separate embeddings storage from full position metadata
**Rationale**: Optimize for semantic search speed while preserving rich context
**Architecture**: FAISS for vectors + MessagePack for metadata (future optimization)

## Performance Characteristics

### Vision Pipeline
- **Latency**: 2.1 seconds total (19x improvement)
- **Accuracy**: 100% on tested positions
- **Throughput**: Suitable for real-time blitz game analysis

### Analysis Engine
- **Response Time**: <1s for cached positions, ~10s for fresh analysis
- **Cache Hit Rate**: >80% for typical viewing sessions
- **Quality**: Expert-level combining engine + historical + human insights

### System Resources
- **Memory**: ~500MB for 100 cached positions
- **CPU**: 76% during vision processing (optimization target)
- **Network**: Dependent on AI service APIs and video streaming

## Data Architecture

### Chess Position Database
**Structure**: Enhanced positions with multi-source analysis
```json
{
  "fen": "position_string",
  "position_features": {...},
  "stockfish_analysis": {...},
  "enhanced_description": "LLM-generated strategic analysis",
  "similar_positions": [...],
  "game_context": {...},
  "selection_reason": "tactical_swing|check|decisive_advantage"
}
```

### Vector Embeddings
**Model**: Gemini-embedding-001 (3072 dimensions)
**Content**: Strategic themes, tactical patterns, position characteristics
**Search**: Cosine similarity with metadata filtering

### Caching Strategy
**Position Cache**: FEN → {white: analysis, black: analysis}
**Scene Cache**: Board masks and broadcast context
**Question History**: Per-position conversation context

## Integration Points

### Input Sources
- **HDMI Video Capture**: Primary for live streams
- **YouTube/Chromecast**: Content control and streaming
- **Audio Transcription**: Commentary context and user voice
- **Broadcast Graphics**: Player info, time pressure, match context

### Output Channels
- **Gemini Live**: Primary conversational interface
- **Audio Synthesis**: Natural voice commentary
- **Debug Visualization**: Development and troubleshooting
- **Memory Storage**: Persistent context and preferences

### External Services
- **Roboflow**: Specialized chess computer vision
- **Google AI**: Gemini models for LLM and embeddings
- **Stockfish**: Chess engine for position evaluation
- **mem0**: Persistent memory and context storage

## Error Handling and Resilience

### Vision Pipeline
- **Graceful Degradation**: Continue operation with vision failures
- **Fallback Strategies**: Multiple detection approaches
- **Validation**: FEN correctness and position legality checks

### Analysis Engine
- **Cache Fallbacks**: On-demand analysis when cache misses
- **API Resilience**: Continue without vector search during service issues
- **Engine Failures**: Template descriptions when LLM enhancement fails

### User Experience
- **Non-blocking Operations**: Background processing doesn't interrupt conversation
- **Timeout Handling**: Reasonable limits with user feedback
- **State Recovery**: Resume operation after temporary failures

## Security and Privacy

### Data Handling
- **Local Processing**: Chess analysis and caching on local system
- **API Communications**: Encrypted connections to AI services
- **User Data**: Voice interactions processed through Google services
- **Memory Storage**: Configurable retention and deletion policies

### Access Control
- **Network Requirements**: Internet access for AI services
- **Device Access**: HDMI capture and Android TV control
- **Service Authentication**: API keys for external services

## Future Architecture Considerations

### Scalability
- **Multi-stream Support**: Parallel analysis of multiple games
- **Cloud Distribution**: Distributed processing for large-scale analysis
- **Local Model Inference**: Reduce API dependencies

### Enhanced Features
- **Opening Preparation**: Integration with opening databases
- **Player Style Analysis**: Characteristic pattern recognition
- **Educational Modes**: Adaptive explanations for different skill levels
- **Tournament Integration**: Live tournament data and context

### Performance Optimization
- **Local Vision Models**: Sub-1s position detection
- **Predictive Caching**: Pre-compute likely next positions
- **Hardware Acceleration**: GPU utilization for analysis pipeline

## Development and Deployment

### Architecture Principles
1. **Separation of Concerns**: Clean module boundaries and responsibilities
2. **Async-First Design**: Non-blocking operations for real-time performance
3. **Error Resilience**: Graceful degradation and recovery strategies
4. **User Experience Priority**: Technical decisions driven by UX requirements
5. **Incremental Enhancement**: Progressive feature addition without breaking changes

### Testing Strategy
- **Component Testing**: Individual module validation
- **Integration Testing**: End-to-end pipeline verification
- **Performance Testing**: Latency and throughput validation
- **User Acceptance**: Real-world usage scenarios

### Deployment Considerations
- **Hardware Requirements**: HDMI capture, sufficient processing power
- **Network Dependencies**: Stable internet for AI services
- **Configuration Management**: API keys and service endpoints
- **Monitoring**: Performance metrics and error tracking

---

*This design document captures the current architecture and key decisions that enable the Chess Companion to provide expert-level chess analysis through natural voice interaction with real-time video streams.*
