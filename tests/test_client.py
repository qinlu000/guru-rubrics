import json
import os
import unittest
from unittest.mock import patch

from buffett_corpus.pipeline.client import complete_json


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class OpenAICompatibleClientTests(unittest.TestCase):
    def test_openai_provider_sends_json_object_request(self):
        response = FakeResponse({
            "choices": [{"message": {"content": '{"principles": []}'}}]
        })
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "test-model",
            "OPENAI_BASE_URL": "https://example.test/v1",
        }, clear=False), patch("buffett_corpus.pipeline.client.urlopen", return_value=response) as request_mock:
            result = complete_json(system="system", user="user", provider="openai")

        self.assertEqual(result, {"principles": []})
        request = request_mock.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/v1/chat/completions")
        self.assertEqual(request.headers["Authorization"], "Bearer test-key")
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["messages"], [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ])
        self.assertEqual(payload["response_format"], {"type": "json_object"})


if __name__ == "__main__":
    unittest.main()
