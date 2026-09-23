from parser.patch_parser import (
    AddedLine,
    extract_added_lines,
)


def test_extract_added_lines():
    patch = """@@ -1,3 +1,5 @@
 def hello():
-    print("old")
+    print("new")
+    return True
"""

    result = extract_added_lines(patch)

    assert result == [
        AddedLine(
            line_number=2,
            content='    print("new")',
        ),
        AddedLine(
            line_number=3,
            content="    return True",
        ),
    ]


def test_ignore_diff_header():
    patch = """@@ -1,2 +1,3 @@
 def hello():
+    return True
"""

    result = extract_added_lines(patch)

    assert result == [
        AddedLine(
            line_number=2,
            content="    return True",
        ),
    ]


def test_deleted_lines_are_not_added_lines():
    patch = """@@ -1,3 +1,2 @@
 def hello():
-    print("old")
     return True
"""

    result = extract_added_lines(patch)

    assert result == []


def test_multiple_hunks():
    patch = """@@ -1,2 +1,3 @@
 def first():
+    return 1

@@ -10,2 +11,3 @@
 def second():
+    return 2
"""

    result = extract_added_lines(patch)

    assert result == [
        AddedLine(
            line_number=2,
            content="    return 1",
        ),
        AddedLine(
            line_number=12,
            content="    return 2",
        ),
    ]


def test_empty_patch():
    result = extract_added_lines("")

    assert result == []
