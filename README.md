# Category-LLD

-> Project Structure

```
project/
|
├── main.py # Entry point of the FastAPI app
│
├── base/ # Reusable base components
│ ├── schema/ # Base Pydantic models (request/response)
│ ├── repository/ # BaseRepository with reusable CRUD operations
│ └── service/ # BaseService that abstracts repository logic
│
├── module/ # Feature modules (e.g : category, expense, etc..)
│ ├── category/ # Example: Category Module
│ │ ├── api/ # API routes
│ │ ├── schema/ # Pydantic request/response models
│ │ ├── models/ # SQLAlchemy models
│ │ ├── repository/ # Module-specific repository (extends BaseRepository)
│ │ └── service/ # Module-specific service (extends BaseService)
│
├── core/ # database settings, logging, etc. 
```

-> Base Repository

- This helps to provide the reusable CRUD operations (create, get, list, update, delete)
- And also supports filtering, sorting, pagination
- The main purpose of Baserepo is designed to be extend in individual modules .

-> Base Service

- This helps to wraps BaseRepository methods and adds validation/business logic.

-> Base Schema

- It has a Standardized request validation and response format which help to use by all the modules.


```category/
  ├── api/              # Contains category-specific routes
  ├── schema/           # Pydantic models
  ├── models/           # SQLAlchemy model: Category
  ├── repository/       # CategoryRepository extending BaseRepository
  └── service/          # CategoryService extending BaseService ```
