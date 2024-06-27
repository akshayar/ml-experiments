import os
import os.path
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.cli.rag import RagCLI
from llama_index.llms.bedrock import Bedrock
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.bedrock import BedrockEmbedding
import chromadb

def get_env_or_default(env_name, default_value):
    if env_name in os.environ:
        return os.environ[env_name]
    else:
        return default_value


region_name=get_env_or_default("AWS_REGION","us-east-1")
embedding_model=get_env_or_default("EMBEDDING_MODEL","amazon.titan-embed-image-v1")
query_model=get_env_or_default("LLM","anthropic.claude-3-sonnet-20240229-v1:0")
print("Region {}, embedding model {}, query model {}".format(region_name,embedding_model,query_model))

vector_store_path="./chroma_db"
document_store_path="./document_store"

if(os.path.isfile(document_store_path)):
    print("file exists")
    docstore = SimpleDocumentStore.from_persist_path(document_store_path)
else:
    print("file doesn't exists")
    docstore = SimpleDocumentStore()

# create client and a new collection
#chroma_client = chromadb.EphemeralClient()
chroma_client = chromadb.PersistentClient(path=vector_store_path)
chroma_collection = chroma_client.get_or_create_collection("quickstart")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

llm = Bedrock(
    model=query_model,  region_name=region_name
)

custom_ingestion_pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        TitleExtractor(llm=llm),
        BedrockEmbedding(model_name=embedding_model, region_name=region_name),
    ],
    vector_store=vector_store,
    docstore=docstore,
    cache=IngestionCache(),
)


# Setting up the custom QueryPipeline is optional!
# You can still customize the vector store, LLM, and ingestion transformations without
# having to customize the QueryPipeline
#custom_query_pipeline = QueryPipeline()
#custom_query_pipeline.add_modules(...)
#custom_query_pipeline.add_link(...)

# you can optionally specify your own custom readers to support additional file types.
#file_extractor = {".html": ...}

rag_cli_instance = RagCLI(
    ingestion_pipeline=custom_ingestion_pipeline,
    llm=llm,  # optional
    #query_pipeline=custom_query_pipeline,  # optional
    #file_extractor=file_extractor,  # optional
)


if __name__ == "__main__":
    rag_cli_instance.cli()
    print("Persisting")
    docstore.persist(persist_path=document_store_path)