import asyncio
import logging
import os
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)
from llama_index.llms.anthropic import Anthropic
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.llms.groq import Groq
from llama_index.core.chat_engine.types import ChatMode
import llm_llamaindex


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(SCRIPT_DIR, "storage")
PDF_DIR = os.path.join(SCRIPT_DIR, "assets")

groqLLM = Groq(model="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))

def ensure_storage_directory():
    if not os.path.exists(PERSIST_DIR):
        try:
            os.makedirs(PERSIST_DIR)
            logger.info(f"Created storage directory: {PERSIST_DIR}")
        except Exception as e:
            logger.error(f"Failed to create storage directory: {str(e)}")
            raise

def log_directory_contents(directory):
    logger.info(f"Contents of {directory}:")
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            logger.info(f"  File: {item} (size: {os.path.getsize(item_path)} bytes)")
        elif os.path.isdir(item_path):
            logger.info(f"  Directory: {item}")

# Global variable to store the Index
pdf_index = None

def process_pdfs(pdf_directory):
    try:
        ensure_storage_directory()
        log_directory_contents(PERSIST_DIR)

        # Check if the PDF directory exists
        if not os.path.exists(pdf_directory):
            logger.error(f"PDF directory {pdf_directory} does not exist.")
            return None

        required_files = ['docstore.json', 'index_store.json']
        # Check if we have a valid existing index
        if all(os.path.exists(os.path.join(PERSIST_DIR, file)) for file in required_files):
            try:
                storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
                index = load_index_from_storage(storage_context)
                logger.info("Successfully loaded existing index.")
                return index
            except Exception as e:
                import traceback
                logger.error(f"Error loading existing index: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.info("Proceeding to create a new index.")

        
        logger.info("Creating new index...")
        documents = SimpleDirectoryReader(pdf_directory).load_data()
        if not documents:
            logger.warning(f"No documents found in {pdf_directory}")
            return None
        
        storage_context = StorageContext.from_defaults(
            docstore=SimpleDocumentStore(),
            index_store=SimpleIndexStore(),
        )
        
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            llm=Anthropic(model="claude-2")
        )
        index.storage_context.persist(
            persist_dir=PERSIST_DIR
        )
        log_directory_contents(PERSIST_DIR)

        return index

    except Exception as e:
        import traceback
        logger.error(f"traceback {traceback.format_exc()}")
        logger.error(f"Error processing PDF: {str(e)}")
        return None

    
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    

# class AssistantFnc(llm.FunctionContext):
#     @llm.ai_callable()
#     async def query_documents(
#         self,
#         question: Annotated[
#             str, llm.TypeInfo(description="The question to ask about the documents")
#         ],
#     ) -> AsyncGenerator[str, None]:
#         """Query the PDF documents for information related to the user's question."""
#         logger.info(f"Querying documents for: {question}")
#         engine = pdf_index.as_query_engine(
#             llm=groqLLM, 
#             similarity_top_k=3
#         )

#         response = engine.query(question)
#         return response


async def initialize_rag():
    global pdf_index
    try:
        pdf_index = await asyncio.to_thread(process_pdfs, PDF_DIR)
        if pdf_index is None:
            logger.error("Failed to create or load index.")
            return False
        return True
    except Exception as e:
        logger.error(f"Error initializing RAG: {str(e)}")
        return False
                
async def entrypoint(ctx: JobContext):

    if not await initialize_rag():
        logger.error("Failed to initialize RAG. Proceeding without it.")
    # fnc_ctx = AssistantFnc()
    initial_chat_ctx = llm.ChatContext().append(
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You have access to information from specific PDF documents. When asked questions, "
            "use the query_documents function to find relevant information. "
            "Provide concise responses and avoid using unpronounceable punctuation."
        ),
        role="system",
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

   

        
    chat_engine = pdf_index.as_chat_engine(
        llm=groqLLM,
        chat_mode=ChatMode.CONTEXT,
    )


    assistant = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=llm_llamaindex.LLM(chat_engine=chat_engine),
        tts=openai.TTS(),
        # fnc_ctx=fnc_ctx,
        chat_ctx=initial_chat_ctx,
    )

    assistant.start(ctx.room, participant)
    # The agent should be polite and greet the user when it joins :)
    await assistant.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            initialize_process_timeout=30,
        ),
    )
