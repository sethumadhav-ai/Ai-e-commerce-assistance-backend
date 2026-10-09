# AI E-Commerce Product Recommendations and Shopping Assistant

AI-based backend system for an e-commerce product recommendation tool and shopping assistant. The project is based on **Python, FastAPI, PostgreSQL, pgvector and Google Gemini embeddings** and it combines conventional product browsing with semantic product search based on the meaning of the query.

## Project Overview

This is a project to develop an intelligent e-commerce website which will allow for products management, user authentication, shopping cart and wishlist operations, order management and AI-based product discovery.

### Current Project Status

**Backend development is currently in progress.** All necessary backend parts, like database setup, product embeddings, and semantic product search have been developed and tested. Other parts of the project are yet to come.

## Technology Stack

| Technology     | Usage                                  |
| -------------- | -------------------------------------- |
| Python         | Programming language                   |
| FastAPI        | REST API development                  |
| PostgreSQL     | Relational database                    |
| SQLAlchemy     | Database object-relational mapper      |
| pgvector       | Vector database                       |
| Google Gemini  | Text embedding generator              |
| Pydantic       | Data validation in API                |
| Alembic        | Database migrations                   |
| JWT            | Authentication architecture           |
| Git and GitHub | Version control software               |

## Features Implemented and Tested

### 1. Product Database

* PostgreSQL database called `ai_ecommerce`
* 12 categories of products
* 904 original products imported to the database
* Product details: name, description, brand, price, stock, rating, category, specification, tags, image URL
* One test product created via the API

### 2. AI Product Embeddings

The text of each product is embedded into the numeric form using `gemini-embedding-001` Google model.

Implemented features are:

* Generation of product embeddings
* Concatenation of product name, description, brand, category, specification, and tags into one string of text to embed
* Storage of embedding data in PostgreSQL
* Storage of vector data using pgvector extension
* Generation of embeddings automatically when creating product through the product API

**Verified result:** all 904 existing products' embeddings have been converted into native 3,072-dimensional vectors. And a newly created test product has received its embedding automatically.

### 3. Semantic Product Search

The API provides for searching products based on the meaning of a search query, rather than on keywords in it.

Examples of the possible queries:

* `headphones for travelling`
* `comfortable shoes for daily walking`
* `electronics for working from home`

The search service creates a vector from the query text and then compares it to the vectors of all products using the cosine distance to rank results by the similarity.

Search functionality includes:

* Semantic similarity ranking
* Minimum and maximum price filter
* Category filter
* Pagination limit
* Exclusion of inactive products

### 4. Vector Database Optimization

* pgvector extension for PostgreSQL was installed
* New native vector column `embedding_vector` with 3,072 dimensions was added
* Existing embedding data was converted into native vector
* HNSW index was created using `halfvec(3072)` with cosine-distance operations

Note: HNSW index has been created, but the existing search query uses full-precision vector column. These two should be aligned in a future optimization step.

### 5. Product API

The following endpoints are available now:

| HTTP Method | Endpoint                    | Usage                                       |
| ----------- | --------------------------- | ------------------------------------------- |
| GET         | `/products/`                | Listing products with pagination and filters |
| POST        | `/products/`                | Creating a product and generating embedding  |
| GET         | `/products/{product_id}`    | Getting a product                           |
| GET         | `/products/semantic-search` | Semantically searching products             |

Product creation and semantic product search functionalities have been verified.

## Additional API Endpoints

Other parts of the application expose the following routes:

### Authentication

* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/me`

### Categories

* `GET /categories/`
* `POST /categories/`
* `GET /categories/{category_id}`

### Shopping Cart

* `GET /cart/`
* `POST /cart/items`
* `PUT /cart/items/{item_id}`
* `DELETE /cart/items/{item_id}`
* `DELETE /cart/`

### Wishlist

* `GET /wishlist/`
* `POST /wishlist/items`
* `DELETE /wishlist/items/{item_id}`
* `DELETE /wishlist/`

### Orders

* `GET /orders/`
* `POST /orders/`
* `GET /orders/{order_id}`

They have been added to the API documentation, but still need to be verified and tested.

## Project Structure

The backend application follows a modular application structure. This is an indicative overview of the application modules created or referenced in it so far. Please refer to the project's repository for a full listing of files.

```text
Ai e-commerce assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   └── product.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   └── product_embedding.py
│   │   └── services/
│   │       ├── embedding_service.py
│   │       └── semantic_search_service.py
│   ├── .env
│   ├── main.py
│   └── venv/
├── .gitignore
└── README.md
```

`.env` file and virtual environment are local development files and must not be added to Git.

## Getting Started

### Prerequisites

Install or configure:

* Python
* PostgreSQL
* pgvector extension for PostgreSQL
* Google Gemini API key
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/sethumadhav-ai/Ai-e-commerce-assistance-backend.git
cd Ai-e-commerce-assistance-backend
```

### 2. Set Up the Python Environment

On Windows Command Prompt:

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

Install the project's dependencies using its dependency file. If the project uses `requirements.txt`, for instance, run:

```cmd
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a local `backend/.env` file with the required environment variables. Use your credentials and keep them secure.

Example of .env file structure:

```dotenv
DATABASE_URL=your_postgresql_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

Use real variable names that are required by the application. Never commit your credentials, API keys or any other sensitive information to GitHub.

### 4. Prepare PostgreSQL

Create `ai_ecommerce` database, set up its connection and ensure that pgvector is installed and active.

If the database has been already configured, do not create it again.

### 5. Start the Backend

In the `backend` directory, while having the virtual environment active:

```cmd
uvicorn main:app --reload
```

### 6. Explore API Documentation

Go to:

http://127.0.0.1:8000/docs

There you will find Swagger UI to inspect available endpoints and perform requests.

## Environment and Security

* Credentials must be stored in environment variables
* Keep .env file out of Git using .gitignore
* Rotate the API key if it has been exposed or committed somewhere
* Use JWT authentication for protected endpoints when needed
* Use test configuration for payment integration
* Validate user inputs and enforce authorization for protected operations

## Work Remaining

The following parts need to be implemented and tested further:

* [ ] Build React frontend with TypeScript and Tailwind CSS
* [ ] Test authentication and authorization
* [ ] Test cart, wishlist and order operations end-to-end
* [ ] Build conversational AI shopping assistant
* [ ] Add personalized recommendations for user's preferences and interactions
* [ ] Implement product comparison
* [ ] Integration and testing of Stripe payments in test mode
* [ ] Add comprehensive automated tests and error handling
* [ ] Align vector search query and index
* [ ] Add or verify Alembic migrations for each database change
* [ ] Prepare Docker configuration and deployment process
* [ ] Finish project documentation and prepare production deployment

## Current Achievements

Main AI-based product search functionality is ready: the application can generate product embeddings, store them in PostgreSQL with pgvector, create embedding for new products and search products semantically.

E-commerce application is in development.

## Author

**Sethu Madhav**

GitHub: https://github.com/sethumadhav-ai
