TOTAL_ROWS = 5418


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_sales_uses_default_pagination(client):
    response = client.get("/sales")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 50
    assert body["total"] == TOTAL_ROWS
    assert len(body["items"]) == 50
    first = body["items"][0]
    assert set(first) == {
        "invoice_no",
        "invoice_date",
        "region",
        "state",
        "dist_code",
        "distributor_name",
        "sku_code",
        "sku_name",
        "brand",
        "channel",
        "qty",
        "net_value",
        "is_return",
    }


def test_list_sales_september_non_returns(client):
    response = client.get(
        "/sales",
        params={
            "is_return": "false",
            "date_from": "2026-09-01",
            "date_to": "2026-09-30",
            "page_size": 1,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 298
    assert len(body["items"]) == 1


def test_list_sales_combined_filters_match_every_row(client):
    response = client.get(
        "/sales",
        params={"region": "North", "channel": "General Trade", "page_size": 200},
    )
    body = response.json()
    assert body["total"] == 944
    assert all(
        item["region"] == "North" and item["channel"] == "General Trade"
        for item in body["items"]
    )


def test_date_to_is_inclusive(client):
    response = client.get(
        "/sales",
        params={"date_from": "2026-09-28", "date_to": "2026-09-28", "page_size": 200},
    )
    body = response.json()
    assert body["total"] > 0
    assert all(item["invoice_date"] == "2026-09-28" for item in body["items"])


def test_pages_do_not_overlap(client):
    page_1 = client.get("/sales", params={"page": 1, "page_size": 20}).json()
    page_2 = client.get("/sales", params={"page": 2, "page_size": 20}).json()
    invoices_1 = {item["invoice_no"] for item in page_1["items"]}
    invoices_2 = {item["invoice_no"] for item in page_2["items"]}
    assert len(invoices_1) == len(invoices_2) == 20
    assert invoices_1.isdisjoint(invoices_2)


def test_last_page_is_partial(client):
    # 5418 rows / 200 per page = 27 full pages + 18 rows on page 28.
    body = client.get("/sales", params={"page": 28, "page_size": 200}).json()
    assert len(body["items"]) == 18
    assert body["total"] == TOTAL_ROWS


def test_page_past_the_end_is_empty(client):
    body = client.get("/sales", params={"page": 999}).json()
    assert body["items"] == []
    assert body["total"] == TOTAL_ROWS


def test_page_size_200_is_allowed(client):
    response = client.get("/sales", params={"page_size": 200})
    assert response.status_code == 200
    assert len(response.json()["items"]) == 200


def test_summary_without_filters(client):
    response = client.get("/sales/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["row_count"] == TOTAL_ROWS
    assert body["net_value"] == 60984552.24
    assert "groups" not in body


def test_summary_grouped_by_region(client):
    body = client.get("/sales/summary", params={"group_by": "region"}).json()
    totals = {group["key"]: group["net_value"] for group in body["groups"]}
    assert totals == {
        "East": 11979450.64,
        "North": 14621494.11,
        "South": 15657120.63,
        "West": 18726486.86,
    }


def test_summary_brand_in_december(client):
    body = client.get(
        "/sales/summary",
        params={
            "brand": "Navratna",
            "date_from": "2025-12-01",
            "date_to": "2025-12-31",
        },
    ).json()
    assert body["net_value"] == 462440.22


def test_summary_grouped_by_month_uses_year_month_keys(client):
    body = client.get("/sales/summary", params={"group_by": "month"}).json()
    keys = [group["key"] for group in body["groups"]]
    assert keys == sorted(keys)
    assert keys[0] == "2025-04"
    assert sum(group["row_count"] for group in body["groups"]) == TOTAL_ROWS


def test_master_data_lists(client):
    assert client.get("/regions").json() == ["East", "North", "South", "West"]
    assert len(client.get("/brands").json()) == 8
    skus = client.get("/skus").json()
    assert len(skus) == 23
    assert set(skus[0]) == {"sku_code", "sku_name", "brand"}
    assert len(client.get("/distributors").json()) == 24
