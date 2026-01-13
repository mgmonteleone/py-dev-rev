---
type: "agent_requested"
description: "Standards and best practices for data modeling using Pydantic v2"
---

# Data Modeling Standards

## Pydantic Models

- **Always use Pydantic models for data validation and serialization**
- Use Pydantic v2 syntax and features (BaseModel, Field, model_validator, computed_field)
- Always use the latest stable pydantic version (v2.x)
- Define explicit field types with proper annotations using modern Python union syntax (`str | None` instead of `Optional[str]`)
- Use `Field()` for validation constraints, defaults, and documentation
- Use `TypeAdapter` for validating non-model types (lists, primitives, etc.)

## Model Design Patterns

### Basic Model Structure

```python
from pydantic import BaseModel, Field, ConfigDict, computed_field
from datetime import datetime, timezone

class UserModel(BaseModel):
    """User data model with validation and serialization.

    Examples:
        >>> user = UserModel(id=1, email="user@example.com", name="John Doe")
        >>> user.full_name
        'John Doe'
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        populate_by_name=True,  # Allow both field names and aliases
        use_enum_values=True,   # Serialize enums as their values
    )

    id: int = Field(..., gt=0, description="Unique user identifier")
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    name: str = Field(..., min_length=1, max_length=100)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when user was created (UTC)"
    )
    updated_at: datetime | None = None

    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display purposes."""
        return self.name.title()
```

### Validation

- Use `field_validator` for single-field validation
- Use `model_validator` for cross-field validation
- Implement custom validators for complex business rules
- Use `BeforeValidator` and `AfterValidator` for transformation pipelines

```python
from pydantic import field_validator, model_validator, ValidationError

class UserModel(BaseModel):
    email: str
    age: int
    password: str
    confirm_password: str

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        """Validate email domain is allowed."""
        if not v.endswith('@company.com'):
            raise ValueError('Email must be from company.com domain')
        return v.lower()

    @model_validator(mode='after')
    def validate_passwords_match(self) -> 'UserModel':
        """Ensure password and confirmation match."""
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
```

#### Error Handling

Always handle `ValidationError` when validating untrusted data:

```python
from pydantic import ValidationError

try:
    user = UserModel(**untrusted_data)
except ValidationError as e:
    # Access structured error information
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}")
    # Or get JSON representation
    print(e.json())
```

### Serialization

- Define `model_dump()` and `model_dump_json()` configurations
- Use `alias` for API field name mappings
- Implement `SerializeAsAny` for polymorphic serialization
- Configure `exclude`, `include`, and `by_alias` as needed
- Use `model_serializer` for custom serialization logic
- Generate JSON schemas with `model_json_schema()` for API documentation

```python
from pydantic import BaseModel, Field, field_serializer

class UserResponse(BaseModel):
    user_id: int = Field(..., alias="id")
    email: str
    created_at: datetime

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        """Serialize datetime as ISO format string."""
        return dt.isoformat()

    # Serialization examples
    def to_dict(self) -> dict:
        """Convert to dictionary with aliases."""
        return self.model_dump(by_alias=True, exclude={'internal_field'})

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(by_alias=True)

    @classmethod
    def get_json_schema(cls) -> dict:
        """Get JSON schema for API documentation."""
        return cls.model_json_schema()
```

## Model Organization

- Group related models in dedicated modules under `models/`
- Create base models for shared fields and configuration
- Use model inheritance for variations (CreateModel, UpdateModel, ResponseModel)
- Define separate request and response models for API boundaries

## Best Practices

- Prefer immutable models with `frozen=True` where appropriate
- Use `Annotated` types for reusable field definitions
- Implement `__str__` and `__repr__` for debugging
- Add comprehensive examples in model docstrings
- Use discriminated unions for polymorphic data structures
- We will commonly be getting data from REST calls, so keep this in mind when designing the objects, you will need helper functions for handling payload data

### Reusable Type Definitions

```python
from typing import Annotated
from pydantic import Field, BaseModel

# Define reusable annotated types
PositiveInt = Annotated[int, Field(gt=0)]
EmailStr = Annotated[str, Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")]
NonEmptyStr = Annotated[str, Field(min_length=1, max_length=255)]

class Product(BaseModel):
    id: PositiveInt
    name: NonEmptyStr
    price: Annotated[float, Field(gt=0, decimal_places=2)]
```

### Discriminated Unions for Polymorphism

```python
from typing import Literal
from pydantic import BaseModel, Field

class SuccessResponse(BaseModel):
    status: Literal["success"] = "success"
    data: dict

class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    message: str
    code: int

# Discriminated union
Response = SuccessResponse | ErrorResponse

def handle_response(response: Response) -> None:
    if response.status == "success":
        # Type checker knows this is SuccessResponse
        print(response.data)
    else:
        # Type checker knows this is ErrorResponse
        print(f"Error {response.code}: {response.message}")
```

### TypeAdapter for Non-Model Validation

```python
from pydantic import TypeAdapter, ValidationError

# Validate lists, primitives, or complex types without creating a model
ListOfInts = TypeAdapter(list[int])
validated_list = ListOfInts.validate_python([1, 2, 3])

# Validate dictionaries with specific structure
DictAdapter = TypeAdapter(dict[str, int])
validated_dict = DictAdapter.validate_python({"a": 1, "b": 2})

# Validate JSON strings
try:
    data = ListOfInts.validate_json('[1, 2, 3]')
except ValidationError as e:
    print(e.errors())
```

### RootModel for Primitive Types

```python
from pydantic import RootModel

class UserList(RootModel[list[UserModel]]):
    """A validated list of users."""

    def get_by_email(self, email: str) -> UserModel | None:
        """Find user by email."""
        for user in self.root:
            if user.email == email:
                return user
        return None

# Usage
users = UserList([user1, user2, user3])
user = users.get_by_email("test@example.com")
```

## Integration with ORMs

- Create separate Pydantic models from ORM models
- Use `model_validate()` for ORM object conversion (replaces deprecated `from_orm()` from Pydantic v1)
- Keep database models and API models decoupled
- We will be reading from BigQuery, and likely writing to Firestore or other document oriented databases

### ORM to Pydantic Conversion

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    """API response model for user data."""
    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode

    id: int
    email: str
    name: str

# Convert ORM object to Pydantic model
def get_user(user_id: int) -> UserResponse:
    orm_user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
    return UserResponse.model_validate(orm_user)
```

### BigQuery Integration

```python
from google.cloud import bigquery
from pydantic import BaseModel, TypeAdapter

class QueryResult(BaseModel):
    """Model for BigQuery query results."""
    user_id: int
    total_purchases: int
    last_purchase_date: datetime

def fetch_from_bigquery(query: str) -> list[QueryResult]:
    """Fetch and validate BigQuery results."""
    client = bigquery.Client()
    rows = client.query(query).result()

    # Convert BigQuery rows to dictionaries and validate
    data = [dict(row) for row in rows]
    adapter = TypeAdapter(list[QueryResult])
    return adapter.validate_python(data)
```

### Firestore Integration

```python
from google.cloud import firestore
from pydantic import BaseModel

class UserDocument(BaseModel):
    """Model for Firestore user documents."""
    email: str
    name: str
    created_at: datetime

    def to_firestore(self) -> dict:
        """Convert to Firestore-compatible dictionary."""
        return self.model_dump(mode='json')

    @classmethod
    def from_firestore(cls, doc_dict: dict) -> 'UserDocument':
        """Create model from Firestore document."""
        return cls.model_validate(doc_dict)

# Usage
db = firestore.Client()
user = UserDocument(email="user@example.com", name="John", created_at=datetime.now(timezone.utc))
db.collection('users').document(user.email).set(user.to_firestore())
```


## Performance Considerations

### Using `model_construct()` for Trusted Data

When you have already-validated data from a trusted source, use `model_construct()` to bypass validation:

```python
# Slow: validates all fields
user = UserModel(**trusted_data)

# Fast: skips validation (use only with trusted data!)
user = UserModel.model_construct(**trusted_data)
```

**Warning**: Only use `model_construct()` with data you trust completely (e.g., from your own database).

### Validation Modes

```python
from pydantic import BaseModel, ValidationError

class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)  # No type coercion
    age: int

# With strict=True, this will fail
try:
    StrictModel(age="25")  # String not allowed
except ValidationError:
    pass

# With strict=False (default), this succeeds
class LaxModel(BaseModel):
    age: int

model = LaxModel(age="25")  # Coerced to int(25)
```

### Lazy Validation

```python
from pydantic import BaseModel, ConfigDict

class LazyModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=False  # Only validate on creation, not on assignment
    )

    name: str

model = LazyModel(name="John")
model.name = 123  # No validation error! Use with caution.
```

## REST API Integration Patterns

Since we commonly receive data from REST calls, here are recommended patterns:

### Request/Response Models

```python
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    email: str = Field(..., description="User email address")
    name: str = Field(..., min_length=1, max_length=100)

class UpdateUserRequest(BaseModel):
    """Request model for updating a user (all fields optional)."""
    email: str | None = None
    name: str | None = None

class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    email: str
    name: str
    created_at: datetime

    @classmethod
    def from_domain(cls, user: UserModel) -> 'UserResponse':
        """Convert domain model to API response."""
        return cls.model_validate(user)
```

### Handling API Payloads

```python
import httpx
from pydantic import TypeAdapter, ValidationError

async def fetch_users_from_api(url: str) -> list[UserResponse]:
    """Fetch and validate users from external API."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        # Validate response data
        adapter = TypeAdapter(list[UserResponse])
        try:
            return adapter.validate_python(response.json())
        except ValidationError as e:
            # Log validation errors and handle gracefully
            print(f"API response validation failed: {e}")
            raise

async def post_user_to_api(url: str, user: CreateUserRequest) -> UserResponse:
    """Post user data to external API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=user.model_dump(mode='json')  # Serialize to JSON-compatible dict
        )
        response.raise_for_status()
        return UserResponse.model_validate(response.json())
```

## Common Patterns Summary

1. **Always use modern Python union type syntax**: `str | None` instead of `Optional[str]`
2. **Use `datetime.now(timezone.utc)`** instead of deprecated `datetime.utcnow()`
3. **Use `model_validate()`** instead of deprecated `from_orm()`
4. **Handle `ValidationError`** when processing untrusted data
5. **Use `TypeAdapter`** for validating non-model types
6. **Use `computed_field`** for derived properties
7. **Use `ConfigDict(from_attributes=True)`** for ORM integration
8. **Separate request/response models** from domain models
9. **Use `model_construct()`** only for trusted, pre-validated data
10. **Generate JSON schemas** with `model_json_schema()` for API documentation