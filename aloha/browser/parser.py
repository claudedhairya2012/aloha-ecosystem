from html.parser import HTMLParser
import json
import re
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional


class FactualContentExtractor(HTMLParser):
    """State-machine HTML parser that strips layout noise while preserving all facts."""

    STRIP_TAGS = {
        "script", "style", "noscript", "svg", "canvas", "iframe",
        "nav", "footer", "aside", "form", "button", "input", "select",
        "textarea", "meta", "link", "object", "embed", "ads", "dialog"
    }

    NOISE_KEYWORDS = {
        "cookie", "banner", "popup", "modal", "newsletter", "subscribe",
        "advert", "promo", "sidebar", "social-share", "comment-section",
        "breadcrumb", "pagination", "menu", "navbar", " tracking"
    }

    BLOCK_TAGS = {
        "p", "div", "section", "article", "main", "header",
        "blockquote", "figcaption", "details", "summary"
    }

    HEADING_TAGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.strip_depth = 0
        self.noise_depth_stack: List[bool] = []

        self.title: str = ""
        self.in_title: bool = False

        self.blocks: List[str] = []
        self.current_buffer: List[str] = []

        self.in_pre: bool = False
        self.in_code: bool = False
        self.list_stack: List[str] = []
        self.list_item_counters: List[int] = []

        self.in_table: bool = False
        self.current_table: List[List[str]] = []
        self.current_row: List[str] = []
        self.current_cell: List[str] = []
        self.in_cell: bool = False

        self.current_heading_prefix: Optional[str] = None
        self.current_link_href: Optional[str] = None
        self.current_link_text: List[str] = []

        self.headings_count = 0
        self.tables_count = 0
        self.code_blocks_count = 0
        self.links_count = 0

    def _is_noise_attrs(self, attrs: List[tuple]) -> bool:
        for k, v in attrs:
            if not v:
                continue
            if k in ("class", "id", "role", "aria-label"):
                v_low = v.lower()
                if v_low in ("navigation", "banner", "contentinfo", "complementary"):
                    return True
                for kw in self.NOISE_KEYWORDS:
                    if kw in v_low:
                        return True
        return False

    def _flush_buffer(self):
        if not self.current_buffer:
            return
        text = "".join(self.current_buffer)
        if not self.in_pre:
            text = re.sub(r"[ \t\r\f\v]+", " ", text).strip()
        if text:
            if self.current_heading_prefix:
                self.blocks.append(f"\n{self.current_heading_prefix} {text}\n")
            else:
                self.blocks.append(text)
        self.current_buffer = []

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        tag = tag.lower()

        if tag == "title":
            self.in_title = True
            return

        if tag in self.STRIP_TAGS:
            self.strip_depth += 1
            return

        is_noise = self._is_noise_attrs(attrs)
        self.noise_depth_stack.append(is_noise)
        if self.strip_depth > 0 or any(self.noise_depth_stack):
            return

        if tag in self.HEADING_TAGS:
            self._flush_buffer()
            self.current_heading_prefix = self.HEADING_TAGS[tag]
            self.headings_count += 1
        elif tag in self.BLOCK_TAGS:
            self._flush_buffer()
        elif tag == "br":
            self.current_buffer.append("\n")
        elif tag == "hr":
            self._flush_buffer()
            self.blocks.append("\n---\n")
        elif tag in ("ul", "ol"):
            self._flush_buffer()
            self.list_stack.append(tag)
            self.list_item_counters.append(0)
        elif tag == "li":
            self._flush_buffer()
            indent = "  " * max(0, len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1] == "ol":
                self.list_item_counters[-1] += 1
                bullet = f"{self.list_item_counters[-1]}. "
            else:
                bullet = "- "
            self.current_buffer.append(f"{indent}{bullet}")
        elif tag == "pre":
            self._flush_buffer()
            self.in_pre = True
            self.code_blocks_count += 1
        elif tag == "code":
            self.in_code = True
            if not self.in_pre:
                self.current_buffer.append("`")
        elif tag in ("strong", "b"):
            self.current_buffer.append("**")
        elif tag in ("em", "i"):
            self.current_buffer.append("*")
        elif tag == "a":
            href = dict(attrs).get("href", "")
            if href and not href.startswith(("javascript:", "#")):
                self.current_link_href = href
                self.current_link_text = []
        elif tag == "table":
            self._flush_buffer()
            self.in_table = True
            self.current_table = []
            self.tables_count += 1
        elif tag == "tr" and self.in_table:
            self.current_row = []
        elif tag in ("td", "th") and self.in_table:
            self.in_cell = True
            self.current_cell = []

    def handle_endtag(self, tag: str):
        tag = tag.lower()

        if tag == "title":
            self.in_title = False
            return

        if tag in self.STRIP_TAGS:
            if self.strip_depth > 0:
                self.strip_depth -= 1
            return

        if self.noise_depth_stack:
            was_noise = self.noise_depth_stack.pop()
            if was_noise or self.strip_depth > 0 or any(self.noise_depth_stack):
                return

        if self.strip_depth > 0:
            return

        if tag in self.HEADING_TAGS:
            self._flush_buffer()
            self.current_heading_prefix = None
        elif tag in self.BLOCK_TAGS or tag == "li":
            self._flush_buffer()
        elif tag in ("ul", "ol"):
            self._flush_buffer()
            if self.list_stack:
                self.list_stack.pop()
                self.list_item_counters.pop()
        elif tag == "pre":
            code_content = "".join(self.current_buffer).strip("\n")
            self.blocks.append(f"\n```\n{code_content}\n```\n")
            self.current_buffer = []
            self.in_pre = False
        elif tag == "code":
            if not self.in_pre:
                self.current_buffer.append("`")
            self.in_code = False
        elif tag in ("strong", "b"):
            self.current_buffer.append("**")
        elif tag in ("em", "i"):
            self.current_buffer.append("*")
        elif tag == "a":
            if self.current_link_href:
                link_label = "".join(self.current_link_text).strip()
                if link_label:
                    self.current_buffer.append(f"[{link_label}]({self.current_link_href})")
                    self.links_count += 1
                self.current_link_href = None
                self.current_link_text = []
        elif tag in ("td", "th") and self.in_table:
            cell_str = re.sub(r"\s+", " ", "".join(self.current_cell)).strip()
            self.current_row.append(cell_str.replace("|", "\\|"))
            self.in_cell = False
        elif tag == "tr" and self.in_table:
            if any(self.current_row):
                self.current_table.append(self.current_row)
        elif tag == "table" and self.in_table:
            self.in_table = False
            md_table = self._render_markdown_table(self.current_table)
            if md_table:
                self.blocks.append(f"\n{md_table}\n")
            self.current_table = []

    def handle_data(self, data: str):
        if self.in_title:
            self.title += data.strip()
            return
        if self.strip_depth > 0 or any(self.noise_depth_stack):
            return
        if self.in_cell:
            self.current_cell.append(data)
            return
        if self.current_link_href is not None:
            self.current_link_text.append(data)
            return
        self.current_buffer.append(data)

    @staticmethod
    def _render_markdown_table(rows: List[List[str]]) -> str:
        if not rows:
            return ""
        max_cols = max(len(r) for r in rows)
        normalized = [r + [""] * (max_cols - len(r)) for r in rows]
        header = "| " + " | ".join(normalized[0]) + " |"
        divider = "| " + " | ".join(["---"] * max_cols) + " |"
        body_lines = ["| " + " | ".join(r) + " |" for r in normalized[1:]]
        return "\n".join([header, divider] + body_lines)


class AlohaHTMLParser:
    """High-efficiency factual parser with built-in direct answer synthesis."""

    @staticmethod
    def _local_extractive_synthesis(body_text: str, title: str, query: str = "") -> str:
        """Deterministic fact-density answer synthesis when offline."""
        clean_lines = [
            line.strip(" -*#")
            for line in body_text.splitlines()
            if len(line.strip()) > 35 and not line.strip().startswith("|")
        ]
        if not clean_lines:
            return ""

        query_terms = {w.lower() for w in re.findall(r"\w{3,}", query or title)}
        scored = []
        for idx, line in enumerate(clean_lines):
            score = 0.0
            if idx == 0:
                score += 2.5
            # Boost lines with factual figures, numbers, percentages, years
            score += len(re.findall(r"\b\d+(?:\.\d+)?%?\b", line)) * 1.8
            low = line.lower()
            for term in query_terms:
                if term in low:
                    score += 2.0
            scored.append((score, idx, line))

        scored.sort(key=lambda x: (-x[0], x[1]))
        top_sentences = [item[2] for item in sorted(scored[:3], key=lambda x: x[1])]
        return " ".join(top_sentences)

    @classmethod
    def _synthesize_direct_answer(cls, body_text: str, title: str, query: str = "") -> str:
        """Formulates a direct, factual answer from the extracted content."""
        context_slice = body_text[:3500].strip()
        if not context_slice or len(context_slice) < 40:
            return ""

        target_topic = query.strip() if query.strip() else title.strip()
        prompt = (
            f"Based strictly on the extracted source data below about '{target_topic}', "
            "write a concise, high-density factual answer (3 to 5 sentences max) followed by "
            "up to 3 key bullet points preserving exact numbers, dates, and technical facts. "
            "Do not use filler introductions.\n\n"
            f"EXTRACTED SOURCE DATA:\n{context_slice}"
        )

        try:
            payload = json.dumps({
                "messages": [
                    {
                        "role": "system",
                        "content": "You are the core synthesis layer of a factual parser. Output direct, accurate Markdown answers grounded strictly in the provided data."
                    },
                    {"role": "user", "content": prompt}
                ],
                "model": "openai",
                "seed": 42
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://text.pollinations.ai/",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "AlohaParser/1.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                synthesized = resp.read().decode("utf-8", errors="ignore").strip()
                if synthesized and len(synthesized) > 25 and "<html" not in synthesized.lower():
                    return synthesized
        except Exception:
            pass

        return cls._local_extractive_synthesis(body_text, title, query)

    def parse_to_markdown(
        self,
        html_content: str,
        source_url: str = "",
        query: str = "",
        synthesize: bool = True
    ) -> Dict[str, Any]:
        raw_html = html_content or ""
        extractor = FactualContentExtractor()
        extractor.feed(raw_html)
        extractor._flush_buffer()

        body_md = "\n\n".join(b for b in extractor.blocks if b.strip())
        body_md = re.sub(r"\n{3,}", "\n\n", body_md).strip()

        title_str = extractor.title.strip() or "Extracted Document"
        header_lines = [f"# {title_str}"]
        if source_url:
            header_lines.append(f"**Source:** `{source_url}`")

        # Native Answer Synthesis directly from the extracted webpage facts
        synthesized_answer = ""
        if synthesize and body_md:
            synthesized_answer = self._synthesize_direct_answer(body_md, title_str, query)

        sections = ["\n".join(header_lines)]
        if synthesized_answer:
            sections.append(f"## Direct Synthesis\n{synthesized_answer}")
        if body_md:
            sections.append(f"## Extracted Source Facts\n{body_md}")

        full_markdown = "\n\n".join(sections).strip()

        raw_chars = max(1, len(raw_html))
        md_chars = len(full_markdown)
        raw_tokens = max(1, raw_chars // 4)
        md_tokens = max(1, md_chars // 4)
        savings_pct = round(max(0.0, (1.0 - (md_chars / raw_chars)) * 100), 1)

        return {
            "title": title_str,
            "source_url": source_url,
            "markdown": full_markdown,
            "raw_markdown": full_markdown,
            "synthesized_answer": synthesized_answer,
            "metadata": {
                "title": title_str,
                "source_url": source_url,
                "headings_extracted": extractor.headings_count,
                "tables_extracted": extractor.tables_count,
                "code_blocks_extracted": extractor.code_blocks_count,
                "links_extracted": extractor.links_count,
            },
            "metrics": {
                "raw_html_chars": raw_chars,
                "markdown_chars": md_chars,
                "raw_estimated_tokens": raw_tokens,
                "clean_estimated_tokens": md_tokens,
                "token_savings_percent": savings_pct,
            }
        }


def parse_html_to_markdown(html_content: str, source_url: str = "", query: str = "") -> Dict[str, Any]:
    """Convenience functional alias for AlohaHTMLParser."""
    parser = AlohaHTMLParser()
    return parser.parse_to_markdown(html_content, source_url=source_url, query=query)
