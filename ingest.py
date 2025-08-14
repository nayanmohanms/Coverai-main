# ingest.py
import os
import uuid
from app import document_parser, llm_client, pinecone_client, db, models
from sqlalchemy.orm import Session

# --- CONFIGURATION ---
DOCUMENTS_DIR = "documents"

def ingest_documents():
    """
    Creates database tables, reads all documents from the DOCUMENTS_DIR, 
    processes them, and upserts them into the Pinecone index.
    """
    print("--- Starting Document Ingestion ---")
    
    # --- FIX: Create database tables if they don't exist ---
    print("Initializing database...")
    models.Base.metadata.create_all(bind=db.engine)
    print("Database initialized.")
    
    # Get a database session
    db_session: Session = next(db.get_db())
    
    # Get a list of files to process
    files_to_process = [f for f in os.listdir(DOCUMENTS_DIR) if os.path.isfile(os.path.join(DOCUMENTS_DIR, f))]
    
    for filename in files_to_process:
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        print(f"\n[1/4] Processing file: {filename}")
        
        try:
            # Check if document is already processed
            existing_doc = db_session.query(models.Document).filter_by(filename=filename).first()
            if existing_doc and existing_doc.status == 'ready':
                print(f"      Skipping '{filename}', already processed.")
                continue

            # Read and parse the document
            with open(filepath, "rb") as f:
                file_content = f.read()
            
            chunks = document_parser.parse_document(file_content, filename)
            if not chunks:
                print(f"      Warning: No text chunks extracted from {filename}. Skipping.")
                continue
            print(f"      Parsed into {len(chunks)} chunks.")

            # Generate embeddings in a batch
            print("[2/4] Generating embeddings...")
            embeddings = llm_client.get_embeddings_batch(chunks)
            print("      Embeddings generated.")

            # Prepare vectors for Pinecone
            print("[3/4] Preparing vectors for Pinecone...")
            vectors_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                if not embedding: continue # Skip if embedding failed
                vector_id = str(uuid.uuid4())
                metadata = {"text": chunk, "source_file": filename} 
                vectors_to_upsert.append((vector_id, embedding, metadata))
            
            # Upsert vectors to Pinecone
            print("[4/4] Upserting vectors to Pinecone...")
            pinecone_client.upsert_vectors(vectors_to_upsert)
            print("      Vectors upserted successfully.")

            # Update database record
            if not existing_doc:
                new_doc = models.Document(filename=filename, status="ready")
                db_session.add(new_doc)
            else:
                existing_doc.status = "ready"
            
            db_session.commit()

        except Exception as e:
            print(f"      ERROR processing {filename}: {e}")
            db_session.rollback()

    print("\n--- Document Ingestion Finished ---")

if __name__ == "__main__":
    ingest_documents()
