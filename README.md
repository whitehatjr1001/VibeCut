# Video Editing Agent 🎬

AI-powered video editing agent that transforms your video clips into polished content using natural language instructions.

## Features

- **Natural Language Video Editing**: Describe what you want, get a finished video
- **Multiple Presets**: Highlights, Reels, and Custom editing modes
- **LangGraph Workflow**: Planner → Retriever → Assembler pipeline
- **VideoDB Integration**: Advanced video search and assembly capabilities
- **Streamlit Interface**: User-friendly web interface

## Quick Start

1. **Clone and Setup**
git clone https://github.com/yourusername/video-editing-agent.git
cd video-editing-agent
pip install -e .

text

2. **Configure Environment**
cp .env.example .env

Add your API keys to .env
text

3. **Run the Application**
streamlit run src/interfaces/streamlit_app.py

text

## Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Planner │───▶│ Retriever │───▶│ Assembler │
│ │ │ │ │ │
│ Creates │ │ Finds & │ │ Creates │
│ execution │ │ selects │ │ final │
│ plan │ │ clips │ │ video │
└─────────────┘ └─────────────┘ └─────────────┘

text

## Development

Install development dependencies
pip install -e ".[dev]"

Run tests
pytest

Format code
black src/

Type checking
mypy src/

text

## Docker Deployment  

docker-compose up --build

text

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
