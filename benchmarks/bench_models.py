"""Benchmarks for Pydantic model operations.

Run with: pytest benchmarks/bench_models.py --benchmark-only
"""

from devrev.models.accounts import Account, AccountsCreateRequest, AccountsListResponse
from devrev.models.works import Work, WorksCreateRequest, WorksListResponse, WorkType


class TestAccountModelBenchmarks:
    """Benchmark account model operations."""

    def test_account_create(self, benchmark, sample_account_data):
        """Benchmark Account model instantiation."""
        benchmark(Account.model_validate, sample_account_data)

    def test_account_dump(self, benchmark, sample_account_data):
        """Benchmark Account model serialization to dict."""
        account = Account.model_validate(sample_account_data)
        benchmark(account.model_dump)

    def test_account_dump_json(self, benchmark, sample_account_data):
        """Benchmark Account model serialization to JSON."""
        account = Account.model_validate(sample_account_data)
        benchmark(account.model_dump_json)

    def test_accounts_list_response(self, benchmark, many_accounts):
        """Benchmark parsing a list response with many accounts."""
        data = {"accounts": many_accounts, "next_cursor": None}
        benchmark(AccountsListResponse.model_validate, data)

    def test_account_create_request(self, benchmark):
        """Benchmark creating an account request."""

        def create_request():
            return AccountsCreateRequest(
                display_name="Test Account",
                domains=["test.com"],
            )

        benchmark(create_request)


class TestWorkModelBenchmarks:
    """Benchmark work model operations."""

    def test_work_create(self, benchmark, sample_work_data):
        """Benchmark Work model instantiation."""
        benchmark(Work.model_validate, sample_work_data)

    def test_work_dump(self, benchmark, sample_work_data):
        """Benchmark Work model serialization to dict."""
        work = Work.model_validate(sample_work_data)
        benchmark(work.model_dump)

    def test_work_dump_json(self, benchmark, sample_work_data):
        """Benchmark Work model serialization to JSON."""
        work = Work.model_validate(sample_work_data)
        benchmark(work.model_dump_json)

    def test_works_list_response(self, benchmark, many_works):
        """Benchmark parsing a list response with many works."""
        data = {"works": many_works, "next_cursor": None}
        benchmark(WorksListResponse.model_validate, data)

    def test_work_create_request(self, benchmark):
        """Benchmark creating a work request."""

        def create_request():
            return WorksCreateRequest(
                type=WorkType.TICKET,
                title="Test Ticket",
                applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
                body="Test body",
            )

        benchmark(create_request)


class TestModelValidationBenchmarks:
    """Benchmark validation overhead."""

    def test_account_with_validation(self, benchmark):
        """Benchmark model creation with validation."""

        def create_with_validation():
            return Account.model_validate(
                {
                    "id": "don:identity:dvrv-us-1:devo/1:account/123",
                    "display_name": "Test",
                    "domains": ["test.com"],
                    "created_date": "2024-01-15T10:30:00Z",
                }
            )

        benchmark(create_with_validation)

    def test_account_construct_no_validation(self, benchmark):
        """Benchmark model creation without validation."""

        def create_without_validation():
            return Account.model_construct(
                id="don:identity:dvrv-us-1:devo/1:account/123",
                display_name="Test",
                domains=["test.com"],
                created_date="2024-01-15T10:30:00Z",
            )

        benchmark(create_without_validation)
