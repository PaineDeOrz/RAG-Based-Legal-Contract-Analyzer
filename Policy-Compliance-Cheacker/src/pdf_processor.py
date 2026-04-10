import os
import json
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np
from config import PDF_DIR, VECTOR_STORE_DIR, CHUNK_SIZE, CHUNK_OVERLAP
import pdfplumber


class PDFProcessor:
    def __init__(self):
        self.vectorizer = None
        self.document_chunks = []
        self.chunk_metadata = []

    def read_pdf_text(self, filepath: str) -> str:
        """Extract text from PDF using pdfplumber"""
        with pdfplumber.open(filepath) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks (word-based for legal docs)"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = ' '.join(chunk_words)
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
                
        return chunks

    def process_documents(self) -> Dict:
        """Process ALL real documents in PDF directory (NO sample generation)"""
        if not os.path.exists(PDF_DIR):
            raise FileNotFoundError(f"❌ No PDF directory found: {PDF_DIR}\n"
                                  f"   Create 'data/pdfs/' and add Contract1.pdf")
        
        documents = []
        metadata = []
        processed_files = []
        
        # Process each document
        for filename in os.listdir(PDF_DIR):
            if filename.endswith(('.txt', '.pdf')):
                filepath = os.path.join(PDF_DIR, filename)
                
                try:
                    if filename.endswith('.pdf'):
                        content = self.read_pdf_text(filepath)
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    if not content.strip():
                        print(f"⚠️  {filename}: Empty/no text extracted, skipping")
                        continue
                    
                    # Create overlapping chunks
                    chunks = self.chunk_text(content)
                    
                    for i, chunk in enumerate(chunks):
                        documents.append(chunk)
                        metadata.append({
                            'filename': filename,
                            'chunk_id': i,
                            'total_chunks': len(chunks),
                            'char_count': len(chunk)
                        })
                    
                    processed_files.append(filename)
                    print(f"✅ Processed {filename}: {len(chunks)} chunks ({len(content):,} chars)")
                    
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")
        
        if not processed_files:
            raise ValueError(f"❌ No valid documents found in {PDF_DIR}\n"
                           f"   Expected: Contract1.pdf or .txt files")
        
        self.document_chunks = documents
        self.chunk_metadata = metadata
        
        return {
            'total_documents': len(set(meta['filename'] for meta in metadata)),
            'total_chunks': len(documents),
            'processed_files': processed_files
        }
    
    def create_vector_store(self):
        """Create multilingual TF-IDF vector store"""
        if not self.document_chunks:
            result = self.process_documents()
            print(f"Processed: {result}")
        
        # Multilingual TF-IDF (no stop_words for German/English mix)
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            # stop_words=None for multilingual (DE/EN legal terms)
            ngram_range=(1, 3),  # 1-3 grams for "Kündigungsfrist", "security deposit"
            min_df=1,
            max_df=0.95,
            lowercase=True,
            token_pattern=r"(?u)\b\w\w+\b"  # Handles German umlauts
        )
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(self.document_chunks)
        
        # Save everything
        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        
        with open(os.path.join(VECTOR_STORE_DIR, 'vectorizer.pkl'), 'wb') as f:
            pickle.dump(self.vectorizer, f)
        with open(os.path.join(VECTOR_STORE_DIR, 'tfidf_matrix.pkl'), 'wb') as f:
            pickle.dump(tfidf_matrix, f)
        with open(os.path.join(VECTOR_STORE_DIR, 'documents.json'), 'w') as f:
            json.dump({
                'chunks': self.document_chunks,
                'metadata': self.chunk_metadata
            }, f, indent=2)
        
        print(f"✅ Vector store created: {len(self.document_chunks)} chunks, "
              f"{len(self.vectorizer.vocabulary_):,} vocab terms")
        return tfidf_matrix
    
    def load_vector_store(self):
        """Load existing vector store (creates if missing)"""
        try:
            with open(os.path.join(VECTOR_STORE_DIR, 'vectorizer.pkl'), 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(os.path.join(VECTOR_STORE_DIR, 'tfidf_matrix.pkl'), 'rb') as f:
                tfidf_matrix = pickle.load(f)
            with open(os.path.join(VECTOR_STORE_DIR, 'documents.json'), 'r') as f:
                data = json.load(f)
                self.document_chunks = data['chunks']
                self.chunk_metadata = data['metadata']
            
            print(f"✅ Vector store loaded: {len(self.document_chunks)} chunks")
            return tfidf_matrix
            
        except FileNotFoundError:
            print("⚠️  Vector store missing, creating from real PDFs...")
            return self.create_vector_store()
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Multilingual semantic search"""
        if self.vectorizer is None:
            self.load_vector_store()
        
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectorizer.transform(self.document_chunks)).flatten()
        
        top_indices = np.argsort(similarities)[::-1][:k]
        results = []
        
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Relevance threshold
                results.append({
                    'content': self.document_chunks[idx],
                    'metadata': self.chunk_metadata[idx],
                    'similarity': float(similarities[idx])
                })
        
        return results


if __name__ == "__main__":
    print("🏠 Processing real rental contracts...")
    processor = PDFProcessor()
    
    # FAILS GRACEFULLY if no PDFs (user must add Contract1.pdf)
    try:
        result = processor.process_documents()
        print(f"\n✅ Processing complete: {result}")
        processor.create_vector_store()
        print("\n🚀 Ready for rental analysis!")
        print("\n📋 Next: python compliance_checker.py")
    except Exception as e:
        print(f"\n❌ {e}")
        print("\n💡 Put Contract1.pdf in data/pdfs/ then re-run")