# app/retrieval.py
from . import llm_client, pinecone_client

def retrieve_and_generate(query: str) -> tuple[str, str]:
    """
    1. Embeds query.
    2. Retrieves relevant context from the entire Pinecone index.
    3. Generates a final answer with an LLM.
    Returns the answer and the formatted context used.
    """
    # 1. Embed the user's query
    query_embedding = llm_client.get_embedding(query)

    # 2. Retrieve relevant chunks from Pinecone (no doc_id needed)
    retrieved_matches = pinecone_client.query_vectors(query_embedding, top_k=5)

    if not retrieved_matches:
        return "Could not find relevant information in the documents.", ""

    # 3. Combine chunks into a single context string, citing the source file
    context_parts = []
    for match in retrieved_matches:
        source = match.get('metadata', {}).get('source_file', 'Unknown Source')
        text = match.get('metadata', {}).get('text', '')
        context_parts.append(f"Source: {source}\n---\n{text}\n---")
    
    context = "\n\n".join(context_parts)

    # 4. Generate the final answer
    answer = llm_client.get_contextual_answer(query, context)

    return answer, context
