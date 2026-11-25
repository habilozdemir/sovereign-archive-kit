#!/usr/bin/env python3
import argparse, glob, hashlib, html, json, operator, os, re, shutil, sys, tarfile, tempfile, zipfile
from datetime import datetime, timezone

TICK = chr(96) * 3

def clean_html(raw_html):
    text = re.sub(r'<h[1-4][^>]*>(.*?)</h[1-4]>', r'\n\n## \1\n\n', raw_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</blockquote>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    lines = [line.strip() for line in html.unescape(text).splitlines()]
    return re.sub(r'\n{3,}', '\n\n', "\n".join(lines)).strip()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest(target_dir):
    entries = []
    for root, _, files in os.walk(target_dir):
        if ".git" in root.split(os.sep):
            continue
        for fn in sorted(files):
            if fn == "MANIFEST.sha256" or fn.startswith("."):
                continue
            full_path = os.path.join(root, fn)
            rel_path = "./" + os.path.relpath(full_path, target_dir).replace("\\", "/")
            entries.append((rel_path, sha256_file(full_path)))
    entries.sort(key=operator.itemgetter(0))
    manifest_path = os.path.join(target_dir, "MANIFEST.sha256")
    with open(manifest_path, "w", encoding="utf-8") as mf:
        for rel, digest in entries:
            mf.write(f"{digest}  {rel}\n")
    return len(entries), sha256_file(manifest_path)

def verify_manifest(target_dir):
    manifest_path = os.path.join(target_dir, "MANIFEST.sha256")
    if not os.path.isfile(manifest_path):
        print(f"ERROR: MANIFEST.sha256 not found in {target_dir}", file=sys.stderr)
        return 1
    ok_count, fail_count = 0, 0
    with open(manifest_path, "r", encoding="utf-8") as mf:
        for line in mf:
            line = line.strip()
            if not line:
                continue
            expected, rel_path = line.split("  ", 1)
            full_path = os.path.join(target_dir, rel_path)
            if not os.path.isfile(full_path):
                print(f"{rel_path}: MISSING")
                fail_count += 1
            elif sha256_file(full_path) == expected:
                print(f"{rel_path}: OK")
                ok_count += 1
            else:
                print(f"{rel_path}: FAILED")
                fail_count += 1
    print(f"\nVerified {ok_count} files ({fail_count} failed).")
    return 0 if fail_count == 0 else 1

def process_medium(zip_path, out_dir):
    raw_dir = tempfile.mkdtemp(prefix="sak_medium_")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(raw_dir)
        os.makedirs(os.path.join(out_dir, "articles-html"), exist_ok=True)
        articles, skipped = [], 0
        for pf in sorted(glob.glob(os.path.join(raw_dir, "**", "posts", "*.html"), recursive=True)):
            fname = os.path.basename(pf)
            with open(pf, "r", encoding="utf-8", errors="replace") as f:
                raw = f.read()
            date_m = re.search(r'<time[^>]*datetime=["\']([^"\']+)["\']', raw, flags=re.IGNORECASE)
            if fname.startswith("draft_") or not date_m:
                skipped += 1
                continue
            title_m = re.search(r'<h1[^>]*>(.*?)</h1>', raw, flags=re.DOTALL | re.IGNORECASE) or re.search(r'<title>(.*?)</title>', raw, flags=re.DOTALL | re.IGNORECASE)
            title = html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1))).strip() if title_m else fname
            shutil.copy2(pf, os.path.join(out_dir, "articles-html", fname))
            articles.append((date_m.group(1), title, fname, clean_html(raw)))
        articles.sort(key=operator.itemgetter(0))
        with open(os.path.join(out_dir, "medium-articles-readable.txt"), "w", encoding="utf-8") as tf:
            for d, t, fn, body in articles:
                tf.write(f"=== ARTICLE: {t} | DATE: {d} | FILE: {fn} ===\n\n{body}\n\n" + ("-" * 60) + "\n\n")
        return f"Medium archive built: {len(articles)} published articles ({skipped} drafts excluded)."
    finally:
        shutil.rmtree(raw_dir, ignore_errors=True)

def process_mastodon(arch_path, out_dir):
    raw_dir = tempfile.mkdtemp(prefix="sak_mastodon_")
    try:
        if arch_path.endswith(".zip"):
            with zipfile.ZipFile(arch_path, "r") as zf:
                zf.extractall(raw_dir)
        else:
            with tarfile.open(arch_path, "r:*") as tf:
                tf.extractall(raw_dir)
        outbox_files = glob.glob(os.path.join(raw_dir, "**", "outbox.json"), recursive=True)
        if not outbox_files:
            raise FileNotFoundError("outbox.json not found in Mastodon archive.")
        with open(next(iter(outbox_files)), "r", encoding="utf-8") as f:
            outbox = json.load(f)
        posts, skipped = [], 0
        for item in outbox.get("orderedItems", []):
            if item.get("type") != "Create":
                continue
            obj = item.get("object", {})
            if not isinstance(obj, dict):
                continue
            rec = " ".join(str(x) for x in (obj.get("to", []) + obj.get("cc", [])))
            if "Public" not in rec and "followers" not in rec:
                skipped += 1
                continue
            posts.append((obj.get("published", ""), obj.get("id", ""), bool(obj.get("inReplyTo")), clean_html(obj.get("content", ""))))
        posts.sort(key=operator.itemgetter(0))
        os.makedirs(os.path.join(out_dir, "media"), exist_ok=True)
        seen, idx = set(), 1
        for root, _, files in os.walk(raw_dir):
            if "media_attachments" in root:
                for fn in sorted(files):
                    if fn.startswith("."):
                        continue
                    src = os.path.join(root, fn)
                    h = sha256_file(src)
                    if h in seen:
                        continue
                    seen.add(h)
                    _, ext = os.path.splitext(fn)
                    shutil.copy2(src, os.path.join(out_dir, "media", f"{idx:03d}_{h}{ext.lower()}"))
                    idx += 1
        with open(os.path.join(out_dir, "mastodon-posts-readable.txt"), "w", encoding="utf-8") as tf:
            for d, pid, is_rep, txt in posts:
                tf.write(f"=== {'REPLY' if is_rep else 'POST'} | DATE: {d} | ID: {pid} ===\n{txt}\n\n")
        return f"Mastodon archive built: {len(posts)} public posts/replies, {idx - 1} media files ({skipped} DMs excluded)."
    finally:
        shutil.rmtree(raw_dir, ignore_errors=True)

def process_nostr(json_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    events = data if isinstance(data, list) else data.get("events", [])
    public_events = sorted([e for e in events if isinstance(e, dict) and e.get("kind") != 4], key=lambda x: x.get("created_at", 0))
    with open(os.path.join(out_dir, "nostr-public-events.json"), "w", encoding="utf-8") as jf:
        json.dump(public_events, jf, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "nostr-posts-readable.txt"), "w", encoding="utf-8") as tf:
        for e in public_events:
            if e.get("kind") in (1, 6, 30023):
                dt = datetime.fromtimestamp(e.get("created_at", 0), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                tf.write(f"=== KIND: {e.get('kind')} | DATE: {dt} | ID: {e.get('id')} ===\n{e.get('content', '')}\n\n")
    return f"Nostr archive built: {len(public_events)} signed public events preserved."

def main():
    parser = argparse.ArgumentParser(description="Sovereign Archive Kit: Convert social exports & folders into SHA-256 verified permanent archives.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("medium", "mastodon", "nostr"):
        p = sub.add_parser(name)
        p.add_argument("input", help="Path to export archive (.zip, .tar.gz, .json)")
        p.add_argument("-o", "--output", default=f"./{name}-archive", help="Output archive directory")
    s_seal = sub.add_parser("seal", help="Generate MANIFEST.sha256 for any existing folder")
    s_seal.add_argument("directory", help="Target directory to seal")
    s_ver = sub.add_parser("verify", help="Verify all files against MANIFEST.sha256")
    s_ver.add_argument("directory", default=".", nargs="?", help="Target archive directory")
    args = parser.parse_args()

    if args.cmd == "seal":
        count, master = generate_manifest(args.directory)
        print(f"Sealed {count} files in {args.directory}\nMaster SHA-256: {master}")
        return
    if args.cmd == "verify":
        sys.exit(verify_manifest(args.directory))

    os.makedirs(args.output, exist_ok=True)
    if args.cmd == "medium":
        msg = process_medium(args.input, args.output)
    elif args.cmd == "mastodon":
        msg = process_mastodon(args.input, args.output)
    else:
        msg = process_nostr(args.input, args.output)

    count, master = generate_manifest(args.output)
    with open(os.path.join(args.output, "README.md"), "w", encoding="utf-8") as rf:
        rf.write(f"# Digital Archive ({args.cmd.capitalize()})\n\n{msg}\n\n- **Verified Files:** {count}\n- **Master SHA-256:** `{master}`\n\n## Verification\n{TICK}bash\npython3 archive_kit.py verify .\n{TICK}\n")
    count, master = generate_manifest(args.output)
    print(f"{msg}\nTotal sealed files: {count}\nMaster SHA-256: {master}")

if __name__ == "__main__":
    main()
