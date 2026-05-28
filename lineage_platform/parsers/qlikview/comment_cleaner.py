import re


class CommentCleaner:
    """
    Remove QlikView comments before parsing.

    Supports:
    - // single-line comments
    - /* multi-line comments */
    """

    SINGLE_LINE_PATTERN = re.compile(r"//.*?$", re.MULTILINE)

    MULTI_LINE_PATTERN = re.compile(r"/\\*.*?\\*/", re.DOTALL)

    @staticmethod
    def clean_comments(script_content: str) -> str:

        # ----------------------------------------------
        # Remove multiline comments
        # ----------------------------------------------

        script_content = CommentCleaner.MULTI_LINE_PATTERN.sub("", script_content)

        # ----------------------------------------------
        # Remove single-line comments
        # ----------------------------------------------

        script_content = CommentCleaner.SINGLE_LINE_PATTERN.sub("", script_content)

        return script_content
