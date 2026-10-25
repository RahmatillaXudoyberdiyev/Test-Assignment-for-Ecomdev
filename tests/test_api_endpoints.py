import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base, get_db_session
from app.main import app


@pytest.fixture
async def test_client():
    """Create test client with isolated in-memory database."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_api_swagger_available(test_client: AsyncClient):
    """Verify Swagger documentation endpoint /api is reachable."""
    response = await test_client.get("/api")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_full_api_flow(test_client: AsyncClient):
    """Verify complete API flow: student CRUD, payment logging, and debtors endpoint."""
    # 1. Create Student
    student_payload = {
        "name": "Rustam Karimov",
        "phone_number": "+998901234567",
        "group": "Frontend-3",
        "monthly_payment_amount": 750000.0,
    }
    create_res = await test_client.post("/students", json=student_payload)
    assert create_res.status_code == 201
    student_data = create_res.json()
    student_id = student_data["id"]
    assert student_data["name"] == "Rustam Karimov"

    # 2. Get Student by ID
    get_res = await test_client.get(f"/students/{student_id}")
    assert get_res.status_code == 200
    assert get_res.json()["group"] == "Frontend-3"

    # 3. List Students
    list_res = await test_client.get("/students")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Check Debtors before payment
    debtors_res = await test_client.get("/debtors")
    assert debtors_res.status_code == 200
    debtors = debtors_res.json()
    assert any(d["student_id"] == student_id and d["debt"] == 750000.0 for d in debtors)

    # 5. Add partial payment
    pay_payload = {
        "student_id": student_id,
        "amount": 250000.0,
    }
    pay_res = await test_client.post("/payments", json=pay_payload)
    assert pay_res.status_code == 201
    assert pay_res.json()["amount"] == 250000.0

    # 6. List payments by student
    student_payments_res = await test_client.get(f"/payments/student/{student_id}")
    assert student_payments_res.status_code == 200
    assert len(student_payments_res.json()) == 1

    # 7. Check Debtors after partial payment
    debtors_res2 = await test_client.get("/debtors")
    assert debtors_res2.status_code == 200
    debtor = next(d for d in debtors_res2.json() if d["student_id"] == student_id)
    assert debtor["total_paid"] == 250000.0
    assert debtor["debt"] == 500000.0

    # 8. Add remaining payment
    await test_client.post("/payments", json={"student_id": student_id, "amount": 500000.0})

    # 9. Check Debtors after full payment (student should not be listed as debtor)
    debtors_res3 = await test_client.get("/debtors")
    assert debtors_res3.status_code == 200
    assert all(d["student_id"] != student_id for d in debtors_res3.json())
