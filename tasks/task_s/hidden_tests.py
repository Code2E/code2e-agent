"""
Task-S hidden tests — 단축 URL 서비스
조건 원문의 기계적 번역. pytest + requests.
실행 중인 서버 대상: BASE_URL 환경변수 (기본 http://localhost:8000)
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def pytest_configure(config):
    config.addinivalue_line("markers", "failure_category(cat): failure category for this test")


def url(path: str) -> str:
    return f"{BASE_URL}{path}"


# ─── C1: POST /shorten with valid URL returns 201 with code ──────────────────

@pytest.mark.failure_category("spec_violation")
def test_C1_post_valid_url_returns_201():
    r = requests.post(url("/shorten"), json={"url": "https://example.com/c1a"})
    assert r.status_code == 201


@pytest.mark.failure_category("spec_violation")
def test_C1_response_contains_code_field():
    r = requests.post(url("/shorten"), json={"url": "https://example.com/c1b"})
    assert r.status_code == 201
    assert "code" in r.json()


@pytest.mark.failure_category("spec_violation")
def test_C1_code_is_alphanumeric_6_to_8_chars():
    r = requests.post(url("/shorten"), json={"url": "https://example.com/c1c"})
    assert r.status_code == 201
    code = r.json()["code"]
    assert 6 <= len(code) <= 8, f"code length {len(code)} not in [6, 8]"
    assert re.fullmatch(r"[A-Za-z0-9]+", code), f"code '{code}' is not alphanumeric"


@pytest.mark.failure_category("spec_violation")
def test_C1_two_different_urls_both_get_codes():
    r1 = requests.post(url("/shorten"), json={"url": "https://example.com/c1d1"})
    r2 = requests.post(url("/shorten"), json={"url": "https://example.com/c1d2"})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert "code" in r1.json()
    assert "code" in r2.json()


# ─── C2: 같은 URL → 항상 동일한 코드 ─────────────────────────────────────────

@pytest.mark.failure_category("spec_violation")
def test_C2_same_url_returns_same_code_on_repeat():
    target = "https://example.com/c2-idempotent"
    r1 = requests.post(url("/shorten"), json={"url": target})
    r2 = requests.post(url("/shorten"), json={"url": target})
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["code"] == r2.json()["code"]


@pytest.mark.failure_category("spec_violation")
def test_C2_third_request_still_same_code():
    target = "https://example.com/c2-triple"
    r1 = requests.post(url("/shorten"), json={"url": target})
    r2 = requests.post(url("/shorten"), json={"url": target})
    r3 = requests.post(url("/shorten"), json={"url": target})
    assert r1.json()["code"] == r2.json()["code"] == r3.json()["code"]


# ─── C3: GET /{code} → 302 redirect to original URL ─────────────────────────

@pytest.mark.failure_category("spec_violation")
def test_C3_get_valid_code_returns_302():
    target = "https://example.com/c3a"
    code = requests.post(url("/shorten"), json={"url": target}).json()["code"]
    r = requests.get(url(f"/{code}"), allow_redirects=False)
    assert r.status_code == 302


@pytest.mark.failure_category("spec_violation")
def test_C3_location_header_matches_original_url():
    target = "https://example.com/c3b"
    code = requests.post(url("/shorten"), json={"url": target}).json()["code"]
    r = requests.get(url(f"/{code}"), allow_redirects=False)
    assert r.status_code == 302
    assert r.headers.get("location") == target or r.headers.get("Location") == target


@pytest.mark.failure_category("spec_violation")
def test_C3_end_to_end_shorten_then_redirect():
    target = "https://example.com/c3c-end-to-end"
    post_r = requests.post(url("/shorten"), json={"url": target})
    assert post_r.status_code == 201
    code = post_r.json()["code"]
    get_r = requests.get(url(f"/{code}"), allow_redirects=False)
    assert get_r.status_code == 302
    location = get_r.headers.get("location") or get_r.headers.get("Location")
    assert location == target


# ─── C4: 유효하지 않은 URL → 400 ─────────────────────────────────────────────

@pytest.mark.failure_category("edge_case")
def test_C4_empty_url_returns_400():
    r = requests.post(url("/shorten"), json={"url": ""})
    assert r.status_code == 400


@pytest.mark.failure_category("edge_case")
def test_C4_non_http_scheme_returns_400():
    r = requests.post(url("/shorten"), json={"url": "ftp://example.com/file"})
    assert r.status_code == 400


# ─── C5: 존재하지 않는 코드 → 404 ─────────────────────────────────────────────

@pytest.mark.failure_category("spec_violation")
def test_C5_nonexistent_code_returns_404():
    r = requests.get(url("/aaaaaaa"), allow_redirects=False)
    assert r.status_code == 404


@pytest.mark.failure_category("spec_violation")
def test_C5_random_string_code_returns_404():
    r = requests.get(url("/zzzzzzz"), allow_redirects=False)
    assert r.status_code == 404
