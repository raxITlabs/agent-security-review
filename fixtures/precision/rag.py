# Precision fixture for scope.rag-without-source-attribution.
# Real retrieval (.invoke on a retriever/vector store, similarity_search) must
# fire; generic `.invoke()` on an LLM / grader / chain must not.

docs = retriever.invoke(query)                   # EXPECT_MATCH
chunks = vectorstore.similarity_search(q)        # EXPECT_MATCH

response = grader_model.invoke(messages)         # EXPECT_NONE
out = llm.invoke(prompt)                          # EXPECT_NONE
reply = chain.invoke(inputs)                      # EXPECT_NONE
