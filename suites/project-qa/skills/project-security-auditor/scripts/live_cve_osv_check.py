#!/usr/bin/env python3
'''Live dependency & framework vulnerability checker querying OSV.dev, NIST NVD CVE 2.0, and CISA KEV.'''

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

IGNORE_DIRS = {
    ".git", ".agents", ".agent", "node_modules", "venv", ".venv", "env",
    "__pycache__", "dist", "build", ".next", ".nuxt", "coverage", "target", "vendor"
}

CORE_FRAMEWORK_HINTS = {
    "next", "react", "vue", "nuxt", "svelte", "@sveltejs/kit", "angular", "@angular/core",
    "express", "fastify", "@nestjs/core", "koa", "hono", "prisma", "@prisma/client",
    "sequelize", "typeorm", "mongoose", "jsonwebtoken", "jose", "next-auth", "better-auth",
    "django", "flask", "fastapi", "starlette", "sqlalchemy", "pydantic", "aiohttp",
    "requests", "urllib3", "cryptography", "pyjwt", "celery", "werkzeug", "jinja2",
    "laravel/framework", "symfony/http-kernel", "gin-gonic/gin", "gofiber/fiber",
    "actix-web", "axum", "tokio", "spring-boot-starter-web"
}


def clean_semver(raw: str) -> str:
    if not raw:
        return ""
    raw = raw.strip().strip("'\"")
    if raw.startswith(("workspace:", "file:", "link:", "git+", "http:", "https:", "*")):
        return ""
    m = re.search(r"(\d+\.\d+(?:\.\d+)?(?:-[0-9A-Za-z.-]+)?)", raw)
    return m.group(1) if m else ""


def collect_dependencies(root_path: str) -> list:
    '''Extract (ecosystem, package_name, version, source_file, pinned_bool) across manifests and lockfiles.'''
    seen = {}

    def record(ecosystem: str, name: str, version: str, rel_file: str, pinned: bool):
        if not name or not version:
            return
        key = (ecosystem, name, version)
        if key not in seen or (pinned and not seen[key]["pinned"]):
            seen[key] = {
                "ecosystem": ecosystem,
                "name": name,
                "version": version,
                "source": rel_file,
                "pinned": pinned,
            }

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            rel = os.path.relpath(full, root_path).replace("\\", "/")
            try:
                if fname == "package-lock.json":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                    for pkg_path, meta in (data.get("packages") or {}).items():
                        if not pkg_path or not isinstance(meta, dict):
                            continue
                        pkg_name = meta.get("name") or pkg_path.split("node_modules/")[-1]
                        ver = clean_semver(str(meta.get("version", "")))
                        if pkg_name and ver:
                            record("npm", pkg_name, ver, rel, True)
                    for pkg_name, meta in (data.get("dependencies") or {}).items():
                        if isinstance(meta, dict):
                            ver = clean_semver(str(meta.get("version", "")))
                            record("npm", pkg_name, ver, rel, True)

                elif fname == "package.json":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                    for section in ("dependencies", "devDependencies"):
                        for pkg_name, spec in (data.get(section) or {}).items():
                            ver = clean_semver(str(spec))
                            pinned = bool(re.match(r"^\d+\.\d+\.\d+$", str(spec).strip()))
                            record("npm", pkg_name, ver, rel, pinned)

                elif fname in ("requirements.txt", "requirements-prod.txt", "requirements-dev.txt"):
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.split("#", 1)[0].strip()
                            if not line or line.startswith("-"):
                                continue
                            m = re.match(r"^([A-Za-z0-9_.\-]+)(?:\[[^\]]+\])?\s*(==|>=|~=)\s*([^;\s,]+)", line)
                            if m:
                                record("PyPI", m.group(1), clean_semver(m.group(3)), rel, m.group(2) == "==")

                elif fname == "poetry.lock":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for block in content.split("[[package]]")[1:]:
                        nm = re.search(r'(?m)^name\s*=\s*"([^"]+)"', block)
                        vr = re.search(r'(?m)^version\s*=\s*"([^"]+)"', block)
                        if nm and vr:
                            record("PyPI", nm.group(1), clean_semver(vr.group(1)), rel, True)

                elif fname == "pyproject.toml":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for m in re.finditer(r'"([A-Za-z0-9_.\-]+)(?:\[[^\]]+\])?\s*(==|>=|~=|!=|\^)\s*([0-9][^"\s,;]*)"', content):
                        record("PyPI", m.group(1), clean_semver(m.group(3)), rel, m.group(2) == "==")

                elif fname == "go.mod":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.split("//", 1)[0].strip()
                            m = re.match(r"^(?:require\s+)?([A-Za-z0-9_.\-/]+)\s+v([0-9][^\s]+)$", line)
                            if m:
                                record("Go", m.group(1), m.group(2), rel, True)

                elif fname == "Cargo.lock":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for block in content.split("[[package]]")[1:]:
                        nm = re.search(r'(?m)^name\s*=\s*"([^"]+)"', block)
                        vr = re.search(r'(?m)^version\s*=\s*"([^"]+)"', block)
                        if nm and vr:
                            record("crates.io", nm.group(1), clean_semver(vr.group(1)), rel, True)

                elif fname == "composer.lock":
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)
                    for section in ("packages", "packages-dev"):
                        for pkg in (data.get(section) or []):
                            nm = pkg.get("name")
                            vr = clean_semver(str(pkg.get("version", "")))
                            record("Packagist", nm, vr, rel, True)

                elif fname == "pom.xml":
                    tree = ET.parse(full)
                    root_el = tree.getroot()
                    ns = {"m": root_el.tag.split("}")[0].strip("{")} if "}" in root_el.tag else {}
                    dep_xpath = ".//m:dependency" if ns else ".//dependency"
                    for dep in root_el.findall(dep_xpath, ns):
                        g = dep.findtext("m:groupId" if ns else "groupId", default="", namespaces=ns).strip()
                        a = dep.findtext("m:artifactId" if ns else "artifactId", default="", namespaces=ns).strip()
                        v = clean_semver(dep.findtext("m:version" if ns else "version", default="", namespaces=ns))
                        if g and a and v and not v.startswith("$"):
                            record("Maven", f"{g}:{a}", v, rel, True)
            except Exception:
                continue

    return list(seen.values())


def http_json(url: str, method: str = "GET", payload: dict = None, timeout: int = 12) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-Security-Auditor/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def extract_fixed_versions(vuln_detail: dict, pkg_name: str) -> list:
    fixes = []
    for aff in vuln_detail.get("affected") or []:
        pkg = (aff.get("package") or {}).get("name", "")
        if pkg and pkg.lower() != pkg_name.lower():
            continue
        for rng in aff.get("ranges") or []:
            for ev in rng.get("events") or []:
                if "fixed" in ev and ev["fixed"] not in fixes:
                    fixes.append(ev["fixed"])
    return fixes


def query_osv_live(deps: list, timeout: int = 12) -> tuple:
    vulns_found = []
    errors = []
    chunk_size = 100

    for idx in range(0, len(deps), chunk_size):
        chunk = deps[idx:idx + chunk_size]
        queries = [
            {"package": {"name": d["name"], "ecosystem": d["ecosystem"]}, "version": d["version"]}
            for d in chunk
        ]
        try:
            batch_resp = http_json("https://api.osv.dev/v1/querybatch", method="POST", payload={"queries": queries}, timeout=timeout)
        except Exception as exc:
            errors.append(f"OSV querybatch failed: {exc}")
            break

        for dep, res in zip(chunk, batch_resp.get("results") or []):
            raw_vulns = res.get("vulns") or []
            for vstub in raw_vulns[:10]:
                vid = vstub.get("id")
                if not vid:
                    continue
                detail = vstub
                try:
                    detail = http_json(f"https://api.osv.dev/v1/vulns/{urllib.parse.quote(vid)}", timeout=timeout)
                except Exception:
                    pass
                aliases = detail.get("aliases") or []
                refs = [r.get("url") for r in (detail.get("references") or []) if r.get("url")][:4]
                db_sev = (detail.get("database_specific") or {}).get("severity", "")
                sev_list = detail.get("severity") or []
                cvss = sev_list[0].get("score", "") if sev_list else ""
                vulns_found.append({
                    "id": vid,
                    "aliases": aliases,
                    "package": dep["name"],
                    "ecosystem": dep["ecosystem"],
                    "installed_version": dep["version"],
                    "version_pinned": dep["pinned"],
                    "source_manifest": dep["source"],
                    "severity": db_sev or cvss or "UNKNOWN",
                    "published": detail.get("published", ""),
                    "modified": detail.get("modified", ""),
                    "summary": (detail.get("summary") or detail.get("details") or "")[:280].strip(),
                    "fixed_versions": extract_fixed_versions(detail, dep["name"]),
                    "references": refs or [f"https://osv.dev/vulnerability/{vid}"],
                })
    return vulns_found, errors


def fetch_cisa_kev_set(timeout: int = 12) -> tuple:
    try:
        data = http_json(
            "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
            timeout=timeout,
        )
        cve_map = {}
        for item in data.get("vulnerabilities") or []:
            cid = item.get("cveID")
            if cid:
                cve_map[cid] = {
                    "dateAdded": item.get("dateAdded"),
                    "vulnerabilityName": item.get("vulnerabilityName"),
                    "requiredAction": item.get("requiredAction"),
                }
        return cve_map, None
    except Exception as exc:
        return {}, f"CISA KEV lookup skipped/failed: {exc}"


def query_nvd_recent_keywords(keywords: list, days: int = 120, timeout: int = 12) -> tuple:
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(days=min(max(days, 1), 120))
    pub_start = start.strftime("%Y-%m-%dT%H:%M:%S.000")
    pub_end = now.strftime("%Y-%m-%dT%H:%M:%S.000")

    advisories = []
    errors = []
    for kw in keywords[:5]:
        params = urllib.parse.urlencode({
            "keywordSearch": kw,
            "pubStartDate": pub_start,
            "pubEndDate": pub_end,
            "resultsPerPage": 8,
        })
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?{params}"
        try:
            resp = http_json(url, timeout=timeout)
            for item in resp.get("vulnerabilities") or []:
                cve = item.get("cve") or {}
                cid = cve.get("id")
                descs = [d.get("value", "") for d in (cve.get("descriptions") or []) if d.get("lang") == "en"]
                metrics = cve.get("metrics") or {}
                score = ""
                severity = ""
                for key in ("cvssMetricV31", "cvssMetricV40", "cvssMetricV30"):
                    if metrics.get(key):
                        cv_data = metrics[key][0].get("cvssData") or {}
                        score = cv_data.get("baseScore", "")
                        severity = cv_data.get("baseSeverity", "")
                        break
                advisories.append({
                    "keyword": kw,
                    "cve_id": cid,
                    "published": cve.get("published", ""),
                    "severity": f"{severity} ({score})".strip(" ()") or "UNRATED",
                    "description": (descs[0] if descs else "")[:260],
                    "url": f"https://nvd.nist.gov/vuln/detail/{cid}" if cid else "",
                })
        except Exception as exc:
            errors.append(f"NVD keyword query '{kw}' failed/rate-limited: {exc}")
    return advisories, errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse project dependencies and query live OSV.dev, CISA KEV, and NIST NVD CVE 2.0 databases for recent security vulnerabilities."
    )
    parser.add_argument("project_dir", nargs="?", default=".", help="Path to target project root (default: current directory)")
    parser.add_argument("--keywords", default="", help="Comma-separated stack keywords for recent NVD CVE search (e.g. nextjs,fastapi,jwt)")
    parser.add_argument("--auto-keywords", action="store_true", help="Automatically infer up to 5 core framework keywords from project dependencies")
    parser.add_argument("--days", type=int, default=120, help="Lookback window in days (1-120) for recent NVD CVE keyword search")
    parser.add_argument("--offline-parse-only", action="store_true", help="Only parse manifests/lockfiles locally without making network requests")
    parser.add_argument("--timeout", type=int, default=12, help="HTTP request timeout in seconds")
    args = parser.parse_args()

    if not os.path.isdir(args.project_dir):
        print(json.dumps({"error": f"Directory not found: {args.project_dir}"}), file=sys.stderr)
        return 1

    deps = collect_dependencies(args.project_dir)
    inferred_keywords = []
    if args.keywords:
        inferred_keywords.extend([k.strip() for k in args.keywords.split(",") if k.strip()])
    if args.auto_keywords:
        for d in deps:
            low = d["name"].lower()
            if low in CORE_FRAMEWORK_HINTS:
                clean_kw = low.split("/")[-1].lstrip("@")
                if clean_kw not in inferred_keywords:
                    inferred_keywords.append(clean_kw)

    report = {
        "project_root": os.path.abspath(args.project_dir),
        "scanned_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dependencies_parsed_count": len(deps),
        "sample_dependencies": deps[:60],
        "selected_stack_keywords": inferred_keywords[:5],
        "live_network_executed": not args.offline_parse_only,
        "osv_vulnerabilities_count": 0,
        "osv_vulnerabilities": [],
        "cisa_kev_matches": [],
        "recent_nvd_keyword_cves": [],
        "warnings": [],
    }

    if args.offline_parse_only:
        print(json.dumps(report, indent=2))
        return 0

    if deps:
        osv_vulns, osv_errs = query_osv_live(deps, timeout=args.timeout)
        report["osv_vulnerabilities"] = osv_vulns
        report["osv_vulnerabilities_count"] = len(osv_vulns)
        report["warnings"].extend(osv_errs)

    kev_map, kev_err = fetch_cisa_kev_set(timeout=args.timeout)
    if kev_err:
        report["warnings"].append(kev_err)

    if kev_map and report["osv_vulnerabilities"]:
        for v in report["osv_vulnerabilities"]:
            candidates = [v["id"]] + list(v.get("aliases") or [])
            for cid in candidates:
                if cid in kev_map:
                    v["cisa_kev_actively_exploited"] = kev_map[cid]
                    report["cisa_kev_matches"].append({"cve_id": cid, "package": v["package"], **kev_map[cid]})

    if inferred_keywords:
        nvd_cves, nvd_errs = query_nvd_recent_keywords(inferred_keywords[:5], days=args.days, timeout=args.timeout)
        for item in nvd_cves:
            if item.get("cve_id") in kev_map:
                item["cisa_kev_actively_exploited"] = True
        report["recent_nvd_keyword_cves"] = nvd_cves
        report["warnings"].extend(nvd_errs)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
