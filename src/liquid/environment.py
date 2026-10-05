class LiquidEnvironment:
    comment_start_delimiter: str = "{#"
    comment_end_delimiter: str = "#}"

    output_start_delimiter: str = "{{"
    output_end_delimiter: str = "}}"

    tag_start_delimiter: str = "{%"
    tag_end_delimiter: str = "%}"

    def __init__(self) -> None:
        pass
