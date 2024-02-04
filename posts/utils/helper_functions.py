from posts.utils.constants import ANIMAL_EMOJIS


def name_with_animal_emoji(name: str) -> str:
    name_char_sum = 0
    name = str(name)
    for _char in name:
        name_char_sum += ord(_char)
    emoji = ANIMAL_EMOJIS[name_char_sum % len(ANIMAL_EMOJIS)]
    return f"{emoji} {name}"
