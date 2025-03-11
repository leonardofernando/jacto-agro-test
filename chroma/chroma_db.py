import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
# from langchain.vectorstores.chroma import Chroma
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from typing import List


CHROMA_PATH = "chroma/chroma_db"
DATA_PATH = "data"


class Embeddings:

    @staticmethod
    def get_embedding_function():
        embeddings = OllamaEmbeddings(model="mistral")  # deepseek-r1:1.5b
        return embeddings


class Chromadb:

    def __init__(self, reset: bool = False):
        self.reset = reset
        self.db = Chroma(
            persist_directory=CHROMA_PATH, embedding_function=Embeddings.get_embedding_function()
        )

    def add_documents(self):
        if self.reset:
            print("Clearing Database")
            self.clear_database()

        # json_documents = self.load_json_documents()
        # json_chunks = self.split_documents(json_documents)

        pdf_documents = self.load_pdf_documents()
        pdf_chunks = self.split_documents(pdf_documents)

        self.add_to_chroma(pdf_chunks)

    @staticmethod
    def load_json_documents():
        weather_list = []
        json_files = os.listdir(f"{DATA_PATH}/json")

        for json_file in json_files:
            json_loader = JSONLoader(
                file_path=f"{DATA_PATH}/json/{json_file}",
                jq_schema=".[]",
                text_content=False
            )
            weather_list.extend(json_loader.load())

        return weather_list

    @staticmethod
    def load_pdf_documents():
        document_loader = PyPDFDirectoryLoader(f"{DATA_PATH}/pdf")
        return document_loader.load()

    @staticmethod
    def split_documents(documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def add_to_chroma(self, chunks: list[Document]):
        chunks_with_ids = self.calculate_chunk_ids(chunks)

        existing_items = self.db.get(include=[])  # IDs sempre serão incluidos por padrão
        existing_ids = set(existing_items["ids"])
        print(f"Quantidade de documentos existentes no DB: {len(existing_ids)}")

        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)

        if len(new_chunks):
            print(f"Adicionando novos documentos: {len(new_chunks)}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            self.db.add_documents(new_chunks, ids=new_chunk_ids)
        else:
            print("Não há documentos novos para serem adicionados.")
        
        print("Concluído!")

    @staticmethod
    def calculate_chunk_ids(chunks):

        last_page_id = None
        current_chunk_index = 0

        for chunk in chunks:
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id

            chunk.metadata["id"] = chunk_id

        return chunks

    @staticmethod
    def clear_database():
        if os.path.exists(CHROMA_PATH):
            shutil.rmtree(CHROMA_PATH)

    def query(self, query_text: str, top_k: int = 3) -> List[str]:
        # results = self.db.similarity_search(query_text, k=top_k)
        # similarity_data = [result.page_content for result in results]
        results = self.db.similarity_search_with_score(query_text, k=top_k)
        similarity_data = [result.page_content for result, _score in results]

        return similarity_data


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    chromadb = Chromadb(reset=args.reset)
    chromadb.add_documents()
