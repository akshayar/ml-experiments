import os
import os.path
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.query_pipeline.query import QueryPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core import ServiceContext, VectorStoreIndex
from llama_index.cli.rag import RagCLI
from llama_index.llms.bedrock import Bedrock
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.query_pipeline import InputComponent
from llama_index.core import Settings
import chromadb
import atexit
import signal
import sys
import boto3


def is_streaming_supported(modelId, region):
    streaming_supported = False
    client = boto3.client('bedrock', region_name=region)
    response = client.get_foundation_model(modelIdentifier=modelId)
    print(response)
    if "modelDetails" in response:
        if "responseStreamingSupported" in response["modelDetails"]:
            streaming_supported = response["modelDetails"]["responseStreamingSupported"]

    if streaming_supported:
        print("Streaming is supported in " + llm_id)
    else:
        print("Streaming is no supported in " + llm_id)

    return streaming_supported


def get_env_or_default(env_name, default_value):
    if env_name in os.environ:
        return os.environ[env_name]
    else:
        return default_value


def signal_handler(sig, frame):
    print('Signal received:', sig)
    shutdown_hook()
    sys.exit(0)


def shutdown_hook():
    print("Shutting down gracefully...")
    if document_store is not None:
        print("Document store Persisting")
        document_store.persist(persist_path=document_store_path)


def create_query_pipeline(ingestion_pipeline, is_streaming_supported):
    retriever = VectorStoreIndex.from_vector_store(
        ingestion_pipeline.vector_store
    ).as_retriever(similarity_top_k=8)
    response_synthesizer = CompactAndRefine(
        streaming=is_streaming_supported, verbose=True
    )
    print(response_synthesizer)
    # define query pipeline
    query_pipeline = QueryPipeline(verbose=False)
    query_pipeline.add_modules(
        {
            "input": InputComponent(),
            "retriever": retriever,
            "summarizer": response_synthesizer,
        }
    )
    query_pipeline.add_link("input", "retriever")
    query_pipeline.add_link("retriever", "summarizer", dest_key="nodes")
    query_pipeline.add_link("input", "summarizer", dest_key="query_str")
    return query_pipeline


# Register the shutdown hook with atexit
atexit.register(shutdown_hook)
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal

vector_store_path = "./chroma_db"
document_store_path = "./document_store"
persist_dir = "./persist_dir"
document_store = None
region_name = get_env_or_default("AWS_REGION", "us-east-1")
embedding_model_id = get_env_or_default("EMBEDDING_MODEL", "amazon.titan-embed-image-v1")
llm_id = get_env_or_default("LLM", "anthropic.claude-3-sonnet-20240229-v1:0")
is_streaming_supported = is_streaming_supported(llm_id, region_name)

print("Region {}, embedding model {}, query model {}".format(region_name, embedding_model_id, llm_id))

if os.path.isfile(document_store_path):
    print("Document store {} exists".format(document_store_path))
    document_store = SimpleDocumentStore.from_persist_path(document_store_path)
else:
    print("Document store {} doesn't exist".format(document_store_path))
    document_store = SimpleDocumentStore()
    document_store.persist(persist_path=document_store_path)

# create client and a new collection
# chroma_client = chromadb.EphemeralClient()
chroma_client = chromadb.PersistentClient(path=vector_store_path)
chroma_collection = chroma_client.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

print("Document Store path {}, Chroma vector DB path {} ".format(document_store_path, vector_store_path))

llm = Bedrock(
    model=llm_id, region_name=region_name
)

embedding_model = BedrockEmbedding(model_name=embedding_model_id, region_name=region_name)

Settings.llm = llm
Settings.embed_model = embedding_model

custom_ingestion_pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        TitleExtractor(llm=llm),
        embedding_model,
    ],
    vector_store=vector_store,
    docstore=document_store,
    cache=IngestionCache(),
)
custom_query_pipeline = create_query_pipeline(custom_ingestion_pipeline, is_streaming_supported)

# Setting up the custom QueryPipeline is optional!
# You can still customize the vector store, LLM, and ingestion transformations without
# having to customize the QueryPipeline
# custom_query_pipeline = QueryPipeline()
# custom_query_pipeline.add_modules(...)
# custom_query_pipeline.add_link(...)

# you can optionally specify your own custom readers to support additional file types.
# file_extractor = {".html": ...}

rag_cli_instance = RagCLI(
    ingestion_pipeline=custom_ingestion_pipeline,
    llm=llm,  # optional
    persist_dir=persist_dir,
    query_pipeline=custom_query_pipeline,  # optional
    # file_extractor=file_extractor,  # optional
)

if __name__ == "__main__":
    try:
        rag_cli_instance.cli()
        print("Document store Persisting")
        document_store.persist(persist_path=document_store_path)
    except EOFError:
        print("EOF received, exiting...")
        shutdown_hook()
        sys.exit(0)
