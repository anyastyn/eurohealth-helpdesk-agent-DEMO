from pathlib import Path

from src.retriever import LocalKnowledgeRetriever


def test_vpn_doc_is_retrieved_from_local_content():
    retriever = LocalKnowledgeRetriever(
        knowledge_dirs=[Path("data/helpdesk")],
        chunk_size=1200,
    )

    results = retriever.search("How do I access VPN?", top_k=2)

    assert results
    assert "vpn-access" in results[0].source_id
