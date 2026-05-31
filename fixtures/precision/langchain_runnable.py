# Precision fixture for LangChain Runnable awareness in the timeout + moderation
# rules. The dominant LangChain LLM shape (ChatOpenAI(...).invoke()) was invisible
# to the raw-SDK-only patterns before.

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

bare = ChatOpenAI(model="gpt-4o")                          # EXPECT_MATCH:scope.llm-call-without-timeout

safe = ChatOpenAI(model="gpt-4o", timeout=30)             # EXPECT_NONE:scope.llm-call-without-timeout
safe_anth = ChatAnthropic(model="claude-3", request_timeout=20)  # EXPECT_NONE:scope.llm-call-without-timeout

def chat_unguarded(msg):
    client = build_client()
    return client.invoke(msg)                             # EXPECT_NONE:stop.llm-provider-missing-moderation

def chat_with_model(msg):
    llm = ChatOpenAI(model="gpt-4o", timeout=10)
    return llm.invoke(msg)                                 # EXPECT_MATCH:stop.llm-provider-missing-moderation

def chat_guarded(msg):
    if guard.classify(msg).flagged:
        return "blocked"
    llm = ChatOpenAI(model="gpt-4o", timeout=10)
    return llm.invoke(msg)                                 # EXPECT_NONE:stop.llm-provider-missing-moderation

def helper(x):
    return x + 1                                           # EXPECT_NONE:stop.llm-provider-missing-moderation
