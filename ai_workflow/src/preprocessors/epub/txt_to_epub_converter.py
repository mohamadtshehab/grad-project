"""
TXT to EPUB converter

Creates a minimal, standards-compliant EPUB (EPUB 3-ish with nav.xhtml and
fallback NCX) from a plain text file. Intended for quick conversions in the
AI workflow or for exporting processed text back to EPUB.
"""

from __future__ import annotations

import os
import zipfile
import uuid
from datetime import datetime
from typing import List, Optional


def _sanitize_filename(name: str) -> str:
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '_')
    return name.strip() or "untitled"


def _split_text_into_chapters(text: str, max_chars: int = 50000) -> List[str]:
    """Split text into roughly equal chapters by paragraph boundaries.

    - Prefers splitting at double newlines.
    - Falls back to hard split if a single paragraph is too large.
    """
    paragraphs = text.replace('\r\n', '\n').split('\n\n')
    chapters: List[str] = []
    current: List[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        # If a single paragraph is huge, flush current and hard-split it
        if para_len > max_chars:
            if current:
                chapters.append('\n\n'.join(current))
                current, current_len = [], 0
            for i in range(0, para_len, max_chars):
                chapters.append(para[i:i + max_chars])
            continue

        # If adding this paragraph exceeds the limit, start a new chapter
        if current_len + para_len + 2 > max_chars and current:  # +2 for the joining newlines
            chapters.append('\n\n'.join(current))
            current, current_len = [para], para_len
        else:
            current.append(para)
            current_len += para_len + 2

    if current:
        chapters.append('\n\n'.join(current))

    # Guarantee at least one chapter
    if not chapters:
        chapters = [text]
    return chapters


def _xhtml_template(title: str, body_html: str, lang: str = 'ar') -> str:
    return (
        f"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        f"<!DOCTYPE html>\n"
        f"<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"{lang}\" lang=\"{lang}\">\n"
        f"<head>\n"
        f"  <meta charset=\"utf-8\"/>\n"
        f"  <title>{title}</title>\n"
        f"</head>\n"
        f"<body>\n{body_html}\n</body>\n"
        f"</html>\n"
    )


def _escape_html(text: str) -> str:
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def _paragraphs_to_html(text: str) -> str:
    # Convert double newlines to paragraphs, single newlines to <br/>
    parts = []
    for para in text.split('\n\n'):
        para_html = _escape_html(para).replace('\n', '<br/>\n')
        parts.append(f"<p>{para_html}</p>")
    return '\n'.join(parts)


def convert_txt_to_epub(
    txt_path: str,
    *,
    title: Optional[str] = None,
    author: Optional[str] = None,
    language: str = 'ar',
    output_dir: Optional[str] = None,
) -> str:
    """Convert a plain text file to an EPUB file.

    Args:
        txt_path: Path to the source .txt file
        title: Optional book title; defaults to filename stem
        author: Optional author metadata
        language: BCP47 language tag, defaults to 'ar'
        output_dir: Target directory for the .epub (defaults next to txt)

    Returns:
        Path to the generated .epub file
    """
    if not os.path.exists(txt_path):
        raise FileNotFoundError(f"TXT file not found: {txt_path}")

    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()

    base_name = os.path.splitext(os.path.basename(txt_path))[0]
    safe_title = _sanitize_filename(title or base_name)
    author = author or "Unknown"
    book_id = f"urn:uuid:{uuid.uuid4()}"

    out_dir = output_dir or os.path.dirname(os.path.abspath(txt_path))
    epub_path = os.path.join(out_dir, f"{safe_title}.epub")

    # Prepare chapters
    chapters = _split_text_into_chapters(text)
    chapter_files = [f"chapter_{i+1}.xhtml" for i in range(len(chapters))]

    # Zip structure:
    # - mimetype (stored, uncompressed)
    # - META-INF/container.xml
    # - OEBPS/content.opf
    # - OEBPS/nav.xhtml
    # - OEBPS/toc.ncx (compat)
    # - OEBPS/chapter_*.xhtml
    with zipfile.ZipFile(epub_path, 'w') as zf:
        # 1) mimetype must be first and uncompressed
        zf.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)

        # 2) container.xml
        container_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<container version=\"1.0\" xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\">\n"
            "  <rootfiles>\n"
            "    <rootfile full-path=\"OEBPS/content.opf\" media-type=\"application/oebps-package+xml\"/>\n"
            "  </rootfiles>\n"
            "</container>\n"
        )
        zf.writestr('META-INF/container.xml', container_xml)

        # 3) Chapters XHTML
        for idx, (chap, chap_file) in enumerate(zip(chapters, chapter_files), start=1):
            chap_html = _paragraphs_to_html(chap)
            xhtml = _xhtml_template(f"{safe_title} - Chapter {idx}", chap_html, lang=language)
            zf.writestr(f"OEBPS/{chap_file}", xhtml)

        # 4) nav.xhtml (EPUB 3 navigation)
        nav_items = '\n'.join(
            [f"      <li><a href=\"{fn}\">Chapter {i+1}</a></li>" for i, fn in enumerate(chapter_files)]
        )
        nav_xhtml = (
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
            "<!DOCTYPE html>\n"
            f"<html xmlns=\"http://www.w3.org/1999/xhtml\" lang=\"{language}\">\n"
            "  <head><meta charset=\"utf-8\"/><title>Navigation</title></head>\n"
            "  <body>\n"
            "    <nav epub:type=\"toc\" id=\"toc\">\n"
            f"      <h1>{_escape_html(safe_title)}</h1>\n"
            "      <ol>\n"
            f"{nav_items}\n"
            "      </ol>\n"
            "    </nav>\n"
            "  </body>\n"
            "</html>\n"
        )
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml)

        # 5) toc.ncx (legacy compatibility)
        ncx_navpoints = '\n'.join(
            [
                (
                    "    <navPoint id=\"navPoint-{i}\" playOrder=\"{i}\">\n"
                    "      <navLabel><text>Chapter {i}</text></navLabel>\n"
                    "      <content src=\"{src}\"/>\n"
                    "    </navPoint>\n"
                ).format(i=i + 1, src=chapter_files[i])
                for i in range(len(chapter_files))
            ]
        )
        toc_ncx = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n"
            f"  <head><meta name=\"dtb:uid\" content=\"{book_id}\"/></head>\n"
            f"  <docTitle><text>{_escape_html(safe_title)}</text></docTitle>\n"
            f"  <navMap>\n{ncx_navpoints}  </navMap>\n"
            "</ncx>\n"
        )
        zf.writestr("OEBPS/toc.ncx", toc_ncx)

        # 6) content.opf
        manifest_items = '\n'.join(
            ["    <item id=\"nav\" href=\"nav.xhtml\" media-type=\"application/xhtml+xml\" properties=\"nav\"/>"]
            + [
                f"    <item id=\"ch{i+1}\" href=\"{fn}\" media-type=\"application/xhtml+xml\"/>"
                for i, fn in enumerate(chapter_files)
            ]
            + ["    <item id=\"ncx\" href=\"toc.ncx\" media-type=\"application/x-dtbncx+xml\"/>"]
        )
        spine_items = '\n'.join([f"    <itemref idref=\"ch{i+1}\"/>" for i in range(len(chapter_files))])
        now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        content_opf = (
            "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
            f"<package xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"bookid\" version=\"3.0\">\n"
            f"  <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">\n"
            f"    <dc:identifier id=\"bookid\">{book_id}</dc:identifier>\n"
            f"    <dc:title>{_escape_html(safe_title)}</dc:title>\n"
            f"    <dc:language>{language}</dc:language>\n"
            f"    <dc:creator>{_escape_html(author)}</dc:creator>\n"
            f"    <meta property=\"dcterms:modified\">{now_iso}</meta>\n"
            f"  </metadata>\n"
            f"  <manifest>\n{manifest_items}\n  </manifest>\n"
            f"  <spine toc=\"ncx\">\n{spine_items}\n  </spine>\n"
            f"</package>\n"
        )
        zf.writestr("OEBPS/content.opf", content_opf)

    return epub_path


if __name__ == "__main__":
    import argparse as _argparse

    cli = _argparse.ArgumentParser(description="Convert TXT to EPUB")
    cli.add_argument("txt_path", help="Path to input .txt file")
    cli.add_argument("--title", help="Book title (defaults to filename)")
    cli.add_argument("--author", help="Author name", default="Unknown")
    cli.add_argument("--language", help="Language (BCP47)", default="ar")
    cli.add_argument("--out-dir", help="Output directory (defaults next to txt)")
    args = cli.parse_args()

    out = convert_txt_to_epub(
        args.txt_path,
        title=args.title,
        author=args.author,
        language=args.language,
        output_dir=args.out_dir,
    )
    print(out)


