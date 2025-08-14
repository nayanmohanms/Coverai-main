# app/llm_client.py
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- BATCH EMBEDDING FUNCTION ---
def get_embeddings_batch(texts: list[str], model="models/embedding-001") -> list[list[float]]:
    """Generates embeddings for a batch of texts, skipping empty strings."""
    non_empty_texts_with_indices = [(i, text) for i, text in enumerate(texts) if text and not text.isspace()]
    if not non_empty_texts_with_indices:
        return [[] for _ in texts]

    original_indices, texts_to_embed = zip(*non_empty_texts_with_indices)

    try:
        result = genai.embed_content(model=model, content=list(texts_to_embed), task_type="RETRIEVAL_DOCUMENT")
        embedding_map = {index: emb for index, emb in zip(original_indices, result['embedding'])}
        final_embeddings = [embedding_map.get(i, []) for i in range(len(texts))]
        return final_embeddings
    except Exception as e:
        print(f"Error in batch embedding: {e}")
        return [[] for _ in texts]


# --- SINGLE EMBEDDING FUNCTION ---
def get_embedding(text: str, model="models/embedding-001") -> list[float]:
    """Generates an embedding for a single text."""
    text = text.replace("\n", " ")
    if not text or text.isspace():
        return []
    result = genai.embed_content(model=model, content=text, task_type="RETRIEVAL_QUERY")
    return result['embedding']


# --- CONTEXTUAL ANSWER FUNCTION ---
def get_contextual_answer(query: str, context: str, model="gemini-1.5-flash-latest") -> str: # <-- CORRECTED MODEL NAME
    """Generates an answer based on the query and provided context using Gemini."""
    
    if not context or context.isspace():
        return "The answer is not available in the provided document because no relevant context was found."

    # Use the corrected model name here
    generative_model = genai.GenerativeModel(model)

    prompt = f"""
    You are an expert assistant for domains like insurance, law, and HR.
    Answer the following question based *only* on the provided context.
    If the answer is not found in the context, say "The answer is not available in the provided document."

    Context:
    ---
    {context}
    ---
    Question: {query}

    Answer:
    """
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        response = generative_model.generate_content(
            prompt,
            safety_settings=safety_settings
        )
        
        if not response.parts:
            block_reason = "Unknown"
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason.name
            return f"Could not generate an answer. The request was blocked by the API for safety reasons: {block_reason}"

        return response.text
    except Exception as e:
        print(f"--- FATAL ERROR DURING CONTENT GENERATION ---")
        print(f"The following error occurred: {e}")
        print("-------------------------------------------")
        return "Sorry, I could not generate an answer due to a critical API issue. Please check the server logs for details."
