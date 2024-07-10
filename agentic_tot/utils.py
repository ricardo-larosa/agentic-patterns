def parse_code_block(text: str):
    """Extracts the first code block.

    Args:
        text (str): The large text containing one or more code blocks.

    Returns:
        str: The first block between ``` and ``` if found, otherwise None.
    """

    start_pattern = r"```"
    end_pattern = r"```"

    in_code_block = False
    code_block = []

    for line in text.splitlines():
        if start_pattern in line:  
            in_code_block = True
            continue  # Skip the line with the start marker

        if in_code_block:
            if end_pattern in line:
                in_code_block = False
                break  # End of the code block
            else:
                code_block.append(line)

    return "\n".join(code_block) if code_block else None
