def build_prompt(topic: str, characters: list[str], duration: int, reference_script: str) -> str:
    character_list = ", ".join(characters) if characters else "no specific characters"

    prompt = f"""
    You are a comedy screenwriter. Your task is to generate a short, funny sketch script suitable for TikTok or Instagram Reels.

    The script should:
    - Be written in proper screenplay format (scene heading, character names, dialogue)
    - Match the tone, pacing, and structure of the following reference sketch:
    ---
    {reference_script}
    ---

    Here are the parameters for the new sketch:
    - **Topic**: {topic or "Any topic you choose"}
    - **Characters**: {character_list}
    - **Target duration**: approximately {duration} seconds

    Only include characters from this list: {character_list}
    Do not invent or include any other characters.

    Output only the script in screenplay format.
    Your output should follow the indentation and spacing conventions exactly.
    Match the structure, layout, and formatting of the reference sketch above.

    Match the layout, indentation, and formatting style of the reference sketch exactly.
    Use spaces to indent characters, dialogue, and parentheticals in the same style.
    Do not invent formatting — match it exactly.

    - Only capitalize a character's name the first time it appears in an action line. For all subsequent mentions in action lines, use normal proper noun capitalization (e.g., "Trevor" not "TREVOR").
    - Character names should always be in ALL CAPS when used as the speaker heading for dialogue.
    """

    return prompt.strip()
