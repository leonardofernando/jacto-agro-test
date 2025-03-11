# Consulta de dados de Cultura Agrícola.

## Arquitetura utilizada:
imagem do excalidraw aqui

## 📌 Requisitos

- Python 3.13+
- Instale Ollama
  - Baixe modelos de LLM, ex: Mistral, DeepSeak, Llama2, etc...
- Instale as dependências necessárias: `$ pip install -r requirements.txt`


# ChromaDB

Este código permite a extração, vetorização e armazenamento de documentos em um banco de dados vetorial utilizando ChromaDB. Ele suporta arquivos **PDF** e **JSON**.

Como rodar:
```sh
$ python script.py 
```

Argumentos opcionais:
 - `--reset`
 - `--json`

Função para adicionar/atualizar documentos:
```python
chromadb = Chromadb(json=args.json, reset=args.reset)
chromadb.add_documents()
```

Função para realizar busca nos dados vetorizados:
```python
chroma_db = Chromadb()
results = chroma_db.query(query_text="text_to_search_in_database")
```

# WeatherAPI

Este código coleta dados climáticos históricos de um local específico utilizando a API WeatherAPI e armazena os dados em um arquivo JSON.

