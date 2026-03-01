from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
import mysql.connector
import os

app = Flask(__name__)

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234', # Change this
    'database': 'ai_search_ecommerce'   # Change this
}

MODEL_PATH = 'final_ecommerce_model'
model = SentenceTransformer(MODEL_PATH)

# --- GLOBAL STORAGE ---
catalog_titles = []
catalog_embeddings = None

def sync_with_db():
    global catalog_titles, catalog_embeddings
    print("🔄 Syncing with MySQL (Enriched Metadata)...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Fetch both Name and Description
        cursor.execute("SELECT name, description FROM products")
        rows = cursor.fetchall()

        # Create an 'enriched' list for the AI to 'read'
        # Example: "Adjustable Walking Cane - Mobility aid stick for seniors to help walking"
        enriched_info = [f"{row[0]} {row[1]}" for row in rows]

        # Keep the original titles for the final display
        catalog_titles = [row[0] for row in rows]

        if enriched_info:
            print(f"🧠 Encoding {len(enriched_info)} products with context...")
            # The AI now calculates math based on the NAME and DESCRIPTION
            catalog_embeddings = model.encode(enriched_info, convert_to_tensor=True)
            print("✅ Sync Complete.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Sync Failed: {e}")

@app.route('/api/ai-search', methods=['POST'])
def search():
    if not catalog_titles:
        return jsonify({"error": "Catalog is empty"}), 500

    data = request.json
    query = data.get('query', '')
    limit = data.get('limit', 5)

    query_emb = model.encode(query, convert_to_tensor=True)
    hits = util.semantic_search(query_emb, catalog_embeddings, top_k=limit)[0]

    results = [{"productName": catalog_titles[hit['corpus_id']],
                "confidenceScore": round(float(hit['score']), 4)} for hit in hits if float(hit['score']) > 0.10]
    return jsonify(results)

# Endpoint to trigger a refresh without restarting the server
@app.route('/api/sync', methods=['GET'])
def trigger_sync():
    sync_with_db()
    print("Synched with db")
    return jsonify({"message": "Sync successful", "count": len(catalog_titles)})

if __name__ == '__main__':
    sync_with_db() # Initial sync on startup
    app.run(host='0.0.0.0', port=5001)