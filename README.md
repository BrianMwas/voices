# LiveKit Voice Assistant with RAG

This project implements a voice assistant using LiveKit's agent framework, incorporating Retrieval-Augmented Generation (RAG) capabilities. The assistant can engage in voice conversations, answer questions based on information from PDF documents, and provide context-aware responses.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Project Structure](#project-structure)
7. [Function Documentation](#function-documentation)
8. [Dependencies](#dependencies)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)

## Overview

This voice assistant leverages various technologies and libraries to provide a seamless voice interaction experience:

- LiveKit for real-time communication
- LlamaIndex for document indexing and querying
- Groq LLM for natural language processing
- Deepgram for speech-to-text conversion
- OpenAI for text-to-speech conversion
- Silero for Voice Activity Detection (VAD)

The assistant can process PDF documents, create a searchable index, and use this information to answer user queries in real-time voice conversations.

## Prerequisites

- Python 3.8+
- LiveKit account and API credentials
- Groq API key
- Deepgram API key
- OpenAI API key

## Installation

1. Clone the repository:
   \`\`\`
   git clone <repository-url>
   cd <project-directory>
   \`\`\`

2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows, use \`venv\\Scripts\\activate\`
   \`\`\`

3. Install the required dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

## Configuration

1. Create a \`.env.local\` file in the project root directory.
2. Add the following environment variables:
   \`\`\`
   GROQ_API_KEY=your_groq_api_key
   DEEPGRAM_API_KEY=your_deepgram_api_key
   OPENAI_API_KEY=your_openai_api_key
   LIVEKIT_API_KEY=your_livekit_api_key
   LIVEKIT_API_SECRET=your_livekit_api_secret
   \`\`\`

3. Place your PDF documents in the \`assets\` directory.

## Usage

To run the voice assistant:

\`\`\`
python main.py
\`\`\`

The assistant will connect to the specified LiveKit room and wait for a participant to join. Once a participant connects, the assistant will greet them and be ready to answer questions based on the indexed PDF documents.

## Project Structure

\`\`\`
.
├── main.py
├── .env.local
├── requirements.txt
├── assets/
│   └── (PDF documents)
├── storage/
│   ├── docstore.json
│   └── index_store.json
└── README.md
\`\`\`

## Function Documentation

### \`ensure_storage_directory()\`
Ensures that the storage directory exists, creating it if necessary.

### \`log_directory_contents(directory: str)\`
Logs the contents of the specified directory, including file sizes and subdirectories.

### \`process_pdfs(pdf_directory: str) -> VectorStoreIndex | None\`
Processes PDF documents in the specified directory, creating or loading a VectorStoreIndex.

- If a valid index exists, it loads the existing index.
- If no valid index exists, it creates a new index from the PDF documents.
- Returns the index or None if an error occurs.

### \`prewarm(proc: JobProcess)\`
Preloads the Voice Activity Detection (VAD) model into the process user data.

### \`initialize_rag() -> bool\`
Initializes the Retrieval-Augmented Generation (RAG) system by processing PDFs and creating the global index.

### \`entrypoint(ctx: JobContext)\`
The main entrypoint for the LiveKit agent. It:
1. Initializes the RAG system
2. Sets up the chat context
3. Connects to the LiveKit room
4. Waits for a participant to join
5. Creates and starts the voice pipeline agent

## Dependencies

- \`livekit.agents\`: Core framework for building LiveKit agents
- \`llama_index\`: Document indexing and querying
- \`anthropic\`: Anthropic's language model integration
- \`groq\`: Groq's language model integration
- \`dotenv\`: Environment variable management
- \`asyncio\`: Asynchronous I/O
- \`logging\`: Logging utilities

## Troubleshooting

- If you encounter issues with index creation, check the \`storage\` directory permissions and ensure all required files are present.
- For API-related errors, verify your API keys in the \`.env.local\` file.
- If the voice assistant is not responding, check the LiveKit room connection and ensure the participant has joined successfully.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.