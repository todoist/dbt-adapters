from types import SimpleNamespace

from .utils import macro_caller

MACROS = "materializations/models/table/create_table_as.sql"


def test_temporary_ctas_passes_its_relation_to_the_adapter():
    calls = []

    def create_table_as(temporary, relation, compiled_code, language, skip_partitioning):
        return f"create table {relation} skip_partitioning={skip_partitioning} as {compiled_code}"

    adapter = SimpleNamespace(
        dispatch=lambda name, package: create_table_as,
        run_query_with_partitions_limit_catching=lambda sql, relation=None: calls.append(
            ("adapter", sql, relation)
        ),
    )
    call = macro_caller(
        MACROS,
        adapter=adapter,
        run_query=lambda sql: calls.append(("run_query", sql)),
        log=lambda message: None,
    )

    result = call("safe_create_table_as", True, "t__dbt_tmp", "select 1")

    assert result == "t__dbt_tmp as temporary relation without partitioning created"
    assert calls == [
        ("adapter", "create table t__dbt_tmp skip_partitioning=True as select 1", "t__dbt_tmp")
    ]
