import unittest

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("GRC Policy-as-Code Dashboard", response.get_data(as_text=True))

    def test_post_evaluation(self):
        response = self.client.post(
            "/",
            data={
                "json_data": '{"resources":[{"type":"aws_s3_bucket","values":{"acl":"public-read"}}]}',
                "rego_data": 'package main\n\ndeny[msg] {\n    r := input.resources[_]\n    r.type == "aws_s3_bucket"\n    r.values.acl == "public-read"\n    msg = "S3 bucket is publicly accessible"\n}',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Violations detected", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
