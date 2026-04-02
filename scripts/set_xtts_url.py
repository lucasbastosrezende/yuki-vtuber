from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Uso: uv run python scripts/set_xtts_url.py https://xxxx.trycloudflare.com/tts_to_audio"
        )
        return 1

    url = sys.argv[1].strip()
    if not url.startswith("http"):
        print("URL invalida.")
        return 1

    conf_path = Path("conf.yaml")
    text = conf_path.read_text(encoding="utf-8")

    for old_model in ["edge_tts", "f5_tts", "gpt_sovits_tts", "x_tts"]:
        text = text.replace(f"    tts_model: '{old_model}'", "    tts_model: 'x_tts'")

    marker = "    x_tts:\n"
    idx = text.find(marker)
    if idx == -1:
        print("Bloco x_tts nao encontrado em conf.yaml")
        return 1

    api_start = text.find("      api_url:", idx)
    api_end = text.find("\n", api_start)
    text = text[:api_start] + f"      api_url: '{url}'" + text[api_end:]

    speaker_start = text.find("      speaker_wav:", idx)
    speaker_end = text.find("\n", speaker_start)
    text = (
        text[:speaker_start]
        + "      speaker_wav: '/content/ref_audio/reference.wav'"
        + text[speaker_end:]
    )

    lang_start = text.find("      language:", idx)
    lang_end = text.find("\n", lang_start)
    text = text[:lang_start] + "      language: 'pt'" + text[lang_end:]

    conf_path.write_text(text, encoding="utf-8")
    print("conf.yaml atualizado para XTTS v2:")
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
