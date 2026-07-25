# Precision fixture for scope.rag-without-source-attribution.
#
# BEFORE (rule v1): anchored on the RETRIEVAL CALL (`docs = retriever.invoke(...)`)
# with a `not: has:` exculpation scoped to the assignment node itself. That check was
# vacuous — an assignment can never contain `.metadata["source"]` in its own subtree —
# so the rule fired on every retrieval call in any codebase, regardless of whether the
# codebase attributed its sources. It produced 4 findings on gpt-researcher (which DOES
# implement report-time citation) and 0 on every repo in fixtures/manifest.yaml.
#
# AFTER (rule v2): anchored on the CONTEXT-ASSEMBLY site — where retrieved content is
# actually rendered into a prompt string — exculpated by provenance (source / url /
# title / metadata) appearing anywhere in the enclosing function, else the module.
#
# The `# AFTER-*` sections below pin that boundary. The `# BEFORE-*` sections pin the
# old false-positive classes so they can never come back.


# ---------------------------------------------------------------------------
# AFTER-POSITIVE: content joined into a prompt context with zero provenance.
# ---------------------------------------------------------------------------

def build_context(docs):
    return "\n".join(d.page_content for d in docs)          # EXPECT_MATCH:scope.rag-without-source-attribution


def build_context_accumulate(docs):
    ctx = ""
    for d in docs:
        ctx += d.page_content                               # EXPECT_MATCH:scope.rag-without-source-attribution
    return ctx


def build_context_fstring(docs):
    out = ""
    for d in docs:
        out = out + f"Chunk: {d.page_content}\n"             # EXPECT_MATCH:scope.rag-without-source-attribution
    return out


def build_context_dict_chunks(chunks):
    return "\n".join(c["raw_content"] for c in chunks)       # EXPECT_MATCH:scope.rag-without-source-attribution


# A comment or docstring that merely TALKS about attribution must not suppress the
# finding — provenance evidence is matched as code nodes, never as raw node text.

def build_context_with_todo(docs):
    # TODO: thread the source url + title metadata through here one day
    return "\n".join(d.page_content for d in docs)          # EXPECT_MATCH:scope.rag-without-source-attribution


def build_context_with_docstring(docs):
    """Compress docs. Should eventually cite the source url of each document."""
    return "\n".join(d.page_content for d in docs)          # EXPECT_MATCH:scope.rag-without-source-attribution


# ---------------------------------------------------------------------------
# AFTER-NEGATIVE: provenance IS rendered alongside the content.
# These are the shapes gpt-researcher actually uses — the regression guard for the
# false accusation that rule v1 shipped.
# ---------------------------------------------------------------------------

def pretty_print_docs(docs, top_n=None):
    # gpt_researcher/prompts.py:553-557 — Source + Title rendered with every chunk.
    return "\n".join(f"Source: {d.metadata.get('source')}\n"
                     f"Title: {d.metadata.get('title')}\n"
                     f"Content: {d.page_content}\n"          # EXPECT_NONE:scope.rag-without-source-attribution
                     for i, d in enumerate(docs)
                     if top_n is None or i < top_n)


def arxiv_scrape_context(docs):
    # gpt_researcher/scraper/arxiv/arxiv.py:25 — attribution in the same f-string.
    context = f"Published: {docs[0].metadata['Published']}; Content: {docs[0].page_content}"  # EXPECT_NONE:scope.rag-without-source-attribution
    return context, docs[0].metadata["Title"]


def web_loader_scrape(docs, extract_title, soup):
    # gpt_researcher/scraper/web_base_loader/web_base_loader.py:30 — `+=` accumulate,
    # but the function also extracts the title, so provenance is threaded.
    content = ""
    for doc in docs:
        content += doc.page_content                          # EXPECT_NONE:scope.rag-without-source-attribution
    title = extract_title(soup)
    return content, title


def dict_chunks_with_source(chunks):
    # Plain (non-f) string provenance evidence must still exculpate.
    return "\n".join(c.get("source", "?") + c["page_content"] for c in chunks)  # EXPECT_NONE:scope.rag-without-source-attribution


# ---------------------------------------------------------------------------
# BEFORE-NEGATIVE: the rule-v1 false-positive class. A retrieval call, on its own,
# is NOT evidence that attribution is missing — v1 fired on all four of these.
# ---------------------------------------------------------------------------

def retrieval_calls_alone(retriever, vectorstore, retriever_instance, query):
    docs = retriever.invoke(query)                           # EXPECT_NONE:scope.rag-without-source-attribution
    chunks = vectorstore.similarity_search(query)            # EXPECT_NONE:scope.rag-without-source-attribution
    more = retriever.get_relevant_documents(query=query)     # EXPECT_NONE:scope.rag-without-source-attribution
    results = retriever_instance.search(max_results=5)       # EXPECT_NONE:scope.rag-without-source-attribution
    return docs, chunks, more, results


# Non-retrieval `.invoke()` on an LLM / grader / chain must stay silent (v1 already
# handled this via the RETRIEVER constraint; keep it pinned).

def llm_invocations(grader_model, llm, chain, messages, prompt, inputs):
    response = grader_model.invoke(messages)                 # EXPECT_NONE:scope.rag-without-source-attribution
    out = llm.invoke(prompt)                                 # EXPECT_NONE:scope.rag-without-source-attribution
    reply = chain.invoke(inputs)                             # EXPECT_NONE:scope.rag-without-source-attribution
    return response, out, reply
