from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: uv run python scripts/set_f5_tts_url.py https://xxxx.trycloudflare.com/tts")
        return 1

    url = sys.argv[1].strip()
    if not url.startswith("http"):
        print("URL invalida.")
        return 1

    conf_path = Path("conf.yaml")
    text = conf_path.read_text(encoding="utf-8")

    text = text.replace("    tts_model: 'edge_tts'", "    tts_model: 'f5_tts'")

    marker = "    f5_tts:\n"
    idx = text.find(marker)
    if idx == -1:
        print("Bloco f5_tts nao encontrado em conf.yaml")
        return 1

    start = text.find("      api_url:", idx)
    end = text.find("\n", start)
    text = text[:start] + f"      api_url: '{url}'" + text[end:]

    conf_path.write_text(text, encoding="utf-8")
    print("conf.yaml atualizado para F5-TTS:")
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
