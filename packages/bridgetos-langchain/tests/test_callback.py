# ABOUTME: Smoke test verifying BridgetOSCallback can be imported and instantiated.
# ABOUTME: Covers structural integrity of the LangChain adapter without a live API.
from bridgetos_langchain import BridgetOSCallback


def test_callback_importable():
    assert BridgetOSCallback is not None
