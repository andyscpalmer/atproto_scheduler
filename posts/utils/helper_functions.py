from posts.utils.constants import ANIMAL_EMOJIS


def get_name_emoji(name: str) -> str:
    name_char_sum = 0
    name = str(name)
    for _char in name:
        name_char_sum += ord(_char)
    emoji = ANIMAL_EMOJIS[name_char_sum % len(ANIMAL_EMOJIS)]
    return emoji


def get_name_with_animal_emoji(name: str) -> str:
    emoji = get_name_emoji(name)
    return f"{emoji} {name}"
