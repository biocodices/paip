from paip.helpers import prettify_JSON_dump


def test_prettify_JSON_dump():
    ugly_JSON = '{"foo":"bar","bam":["baz","qux"]}'
    result = prettify_JSON_dump(ugly_JSON)
    assert result == \
"""{
  "foo": "bar",
  "bam": [
    "baz",
    "qux"
  ]
}"""
