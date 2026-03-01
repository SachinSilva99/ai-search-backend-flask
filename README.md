# 🤖 AI-Powered Semantic Product Search — Flask Microservice

> Python Flask microservice that serves a fine-tuned Sentence Transformer model for semantic product search in an e-commerce platform.

---

## 🚀 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Runtime environment |
| **Flask** | 3.x | Lightweight web framework |
| **Flask-CORS** | 4.x | Cross-origin request handling |
| **Sentence Transformers** | 2.x | Semantic embedding generation |
| **PyTorch** | 2.x | Deep learning backend |
| **NumPy** | 1.x | Numerical computations |
| **MySQL Connector** | 8.x | Database connectivity for product sync |

---

## ✨ Features

- 🔍 **Semantic Product Search** — Accepts natural language queries and returns semantically relevant products ranked by confidence score
- 🧠 **Fine-Tuned Model** — Uses a custom fine-tuned `all-MiniLM-L6-v2` Sentence Transformer model (22.7M parameters, 384-dim embeddings)
- 📊 **Confidence Scoring** — Returns cosine similarity scores for each result, filtered by a minimum threshold of 0.10
- 🔄 **Database Sync** — `/api/sync` endpoint to refresh the product catalog and re-compute embeddings from the MySQL database
- ⚡ **Pre-computed Embeddings** — Product embeddings are computed once at startup/sync and stored in memory for fast search
- 🌐 **CORS Enabled** — Allows cross-origin requests from the Angular frontend and Spring Boot backend

---

## 📁 Project Structure

```
ai-search-flask/
├── main.py                          # Flask application entry point
│                                    #   - Model & embedding loading
│                                    #   - /api/ai-search (POST)
│                                    #   - /api/sync (GET)
│                                    #   - MySQL product sync logic
├── final_ecommerce_model/           # Fine-tuned model directory
│   ├── config.json                  # Model architecture config
│   ├── config_sentence_transformers.json
│   ├── model.safetensors            # Model weights (22.7M params)
│   ├── tokenizer.json               # WordPiece tokenizer
│   ├── tokenizer_config.json        # Tokenizer settings
│   ├── special_tokens_map.json      # [CLS], [SEP], [PAD] mappings
│   ├── vocab.txt                    # Vocabulary file (30,522 tokens)
│   ├── modules.json                 # Sentence Transformer pipeline
│   ├── 1_Pooling/                   # Mean pooling configuration
│   └── sentence_bert_config.json    # SBERT configuration
├── ai-search-dataset.csv            # Original training dataset (50K rows)
├── ai-search-dataset-diverse.csv    # Augmented dataset (bias-corrected)
└── requirements.txt                 # Python dependencies
```

---

## ⚙️ Prerequisites

- **Python** 3.10 or higher
- **pip** (Python package manager)
- **MySQL Server** 8.x running with `ecommerce_db` database populated
- **CUDA** (optional) — GPU support for faster inference

---

## 🏁 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-search-flask.git
cd ai-search-flask
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

### 3. Install dependencies
```bash
pip install flask flask-cors sentence-transformers torch numpy mysql-connector-python
```

### 4. Configure database connection
Edit the database credentials in `main.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'ecommerce_db'
}
```

### 5. Start the Flask server
```bash
python main.py
```
The server will start at `http://localhost:5001/`.

On startup, the service will:
1. Load the fine-tuned Sentence Transformer model from `./final_ecommerce_model`
2. Connect to MySQL and fetch all product names and descriptions
3. Pre-compute 384-dimensional embeddings for the entire product catalog
4. Begin serving search requests

---

## 📡 API Endpoints

### 1. Semantic Search

**`POST /api/ai-search`**

Search for products using natural language queries.

**Request:**
```json
{
  "query": "something to keep my drinks cold while camping",
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "product_name": "Insulated Water Bottle",
      "confidence": 0.847
    },
    {
      "product_name": "Portable Cooler Box",
      "confidence": 0.793
    },
    {
      "product_name": "Thermos Flask 1L",
      "confidence": 0.651
    }
  ],
  "query": "something to keep my drinks cold while camping",
  "total_results": 3
}
```

> **Note:** Only results with a confidence score above **0.10** are returned. Results are sorted by confidence in descending order.

---

### 2. Product Catalog Sync

**`GET /api/sync`**

Triggers a re-sync of the product catalog from the MySQL database. This re-fetches all product names and descriptions and re-computes their embeddings.

**Response:**
```json
{
  "status": "success",
  "products_synced": 150
}
```

> **When to use:** Call this endpoint after adding, updating, or deleting products through the admin panel to ensure the AI search index is up to date.

---

## 🧠 Model Details

| Property | Value |
|---|---|
| **Base Model** | `all-MiniLM-L6-v2` (Microsoft) |
| **Parameters** | 22.7 million |
| **Embedding Dimensions** | 384 |
| **Max Sequence Length** | 256 tokens |
| **Training Method** | Fine-tuned with `CosineSimilarityLoss` |
| **Training Data** | 50,000+ query–product pairs (4 categories) |
| **Training Epochs** | 3 |
| **Similarity Function** | Cosine similarity |
| **Confidence Threshold** | 0.10 (minimum) |

### How It Works

1. **Query Encoding** — The user's natural language query is tokenised and encoded into a 384-dimensional embedding vector using the fine-tuned model.
2. **Catalog Embeddings** — All product names and descriptions are pre-encoded into embedding vectors at startup.
3. **Cosine Similarity** — The query embedding is compared against all catalog embeddings using `sentence_transformers.util.semantic_search()`.
4. **Ranking & Filtering** — Results are ranked by similarity score and filtered to include only those above the 0.10 confidence threshold.
5. **Response** — The top-k results (default: 10) are returned with product names and confidence scores.

---

## 🔗 Integration with Spring Boot

The Flask service is called by the Spring Boot backend's `AiSearchService` via **WebClient** (reactive HTTP client):

```
Customer → Angular → Spring Boot (SearchController)
                          ↓
                    AiSearchService
                          ↓ (WebClient POST)
                    Flask /api/ai-search
                          ↓
                    Sentence Transformer Model
                          ↓
                    Ranked Results → Spring Boot
                          ↓ (enrich with DB data)
                    Full Product Details → Angular → Customer
```

> The Angular frontend **never calls Flask directly**. All search requests are proxied through the Spring Boot backend, which enriches the AI results with full product details (price, image, category) from the MySQL database.

---

## 📊 Dataset

| File | Rows | Description |
|---|---|---|
| `ai-search-dataset.csv` | ~50,000 | Original training dataset |
| `ai-search-dataset-diverse.csv` | ~55,000 | Augmented dataset with bias correction |

**Columns:**
| Column | Type | Description |
|---|---|---|
| `natural_query` | string | Natural language search query |
| `product_title` | string | Target product name |
| `category_code` | string | Product category (ELECTRONICS, KITCHEN, CLOTHING, HEALTH) |
| `relevance_score` | float | Relevance score (0.0 – 1.0) |

---

## 🛠️ Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: sentence_transformers` | Run `pip install sentence-transformers` |
| `torch` not found | Run `pip install torch` (use CPU version if no GPU) |
| MySQL connection error | Verify MySQL is running and credentials in `main.py` are correct |
| Model loading slow | First load downloads tokenizer files; subsequent loads use cache |
| Low search accuracy | Run `/api/sync` to refresh embeddings after product catalog changes |

---

## 📄 License

This project is part of a BSc Final Year Project at ICBT Campus.
