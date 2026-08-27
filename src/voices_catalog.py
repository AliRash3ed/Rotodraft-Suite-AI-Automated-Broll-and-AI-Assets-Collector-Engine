import json
import asyncio
import edge_tts
from pathlib import Path
from typing import List, Dict, Any, Optional

RECOMMENDED_VOICES = {
    # Top Viral / High-Retention voices
    "en-US-ChristopherNeural": {"label": "⭐ Christopher (Deep Storyteller / MrBeast Style)", "score": 99},
    "en-US-GuyNeural": {"label": "⭐ Guy (Energetic / YouTube Explainer)", "score": 97},
    "en-US-JennyNeural": {"label": "⭐ Jenny (Natural Female / Viral TikTok)", "score": 98},
    "en-US-AriaNeural": {"label": "⭐ Aria (Professional / High Energy)", "score": 96},
    "en-US-EricNeural": {"label": "Eric (Conversational Male)", "score": 92},
    "en-GB-RyanNeural": {"label": "⭐ Ryan (Cinematic British / BBC Documentary)", "score": 99},
    "en-GB-SoniaNeural": {"label": "⭐ Sonia (Polished British Female)", "score": 95},
    "en-AU-WilliamNeural": {"label": "William (Australian Male)", "score": 90},
    "ur-PK-AsadNeural": {"label": "⭐ Asad (Urdu Deep Voiceover / News)", "score": 99},
    "ur-PK-UzmaNeural": {"label": "⭐ Uzma (Urdu Clear Female)", "score": 95},
    "hi-IN-MadhurNeural": {"label": "⭐ Madhur (Hindi Storyteller / YouTube)", "score": 99},
    "hi-IN-SwaraNeural": {"label": "⭐ Swara (Hindi Smooth Female)", "score": 96},
    "ar-SA-HamedNeural": {"label": "⭐ Hamed (Arabic Classical / Documentary)", "score": 98},
    "ar-SA-ZariyahNeural": {"label": "⭐ Zariyah (Arabic Modern Female)", "score": 95},
    "es-ES-AlvaroNeural": {"label": "⭐ Alvaro (Spanish European Male)", "score": 97},
    "es-MX-DaliaNeural": {"label": "⭐ Dalia (Spanish Latin American Female)", "score": 97},
    "fr-FR-HenriNeural": {"label": "⭐ Henri (French Cinematic Male)", "score": 96},
    "de-DE-ConradNeural": {"label": "⭐ Conrad (German Authority Male)", "score": 96},
    "ja-JP-KeitaNeural": {"label": "⭐ Keita (Japanese Anime / Documentary)", "score": 97},
    "pt-BR-AntonioNeural": {"label": "⭐ Antonio (Portuguese Brazil Male)", "score": 97},
    "it-IT-DiegoNeural": {"label": "⭐ Diego (Italian Expressive Male)", "score": 96},
    "tr-TR-AhmetNeural": {"label": "⭐ Ahmet (Turkish Strong Male)", "score": 96},
    "zh-CN-YunxiNeural": {"label": "⭐ Yunxi (Chinese Male Storyteller)", "score": 98},
    "ru-RU-DmitryNeural": {"label": "⭐ Dmitry (Russian Deep Male)", "score": 96}
}

LANGUAGE_NAMES = {
    "en-US": "English (United States)",
    "en-GB": "English (United Kingdom)",
    "en-AU": "English (Australia)",
    "en-CA": "English (Canada)",
    "en-IN": "English (India)",
    "ur-PK": "Urdu (Pakistan)",
    "hi-IN": "Hindi (India)",
    "ar-SA": "Arabic (Saudi Arabia)",
    "ar-EG": "Arabic (Egypt)",
    "es-ES": "Spanish (Spain)",
    "es-MX": "Spanish (Mexico)",
    "fr-FR": "French (France)",
    "fr-CA": "French (Canada)",
    "de-DE": "German (Germany)",
    "it-IT": "Italian (Italy)",
    "ja-JP": "Japanese (Japan)",
    "ko-KR": "Korean (South Korea)",
    "pt-BR": "Portuguese (Brazil)",
    "ru-RU": "Russian (Russia)",
    "tr-TR": "Turkish (Turkey)",
    "zh-CN": "Chinese (Mandarin Simplified)",
    "id-ID": "Indonesian (Indonesia)",
    "nl-NL": "Dutch (Netherlands)",
    "pl-PL": "Polish (Poland)",
    "sv-SE": "Swedish (Sweden)",
    "vi-VN": "Vietnamese (Vietnam)"
}

class VoiceCatalog:
    _cached_voices: Optional[List[Dict[str, Any]]] = None

    @classmethod
    async def get_all_voices(cls) -> List[Dict[str, Any]]:
        """Fetches and enriches all 320+ Edge-TTS Microsoft Neural voices."""
        if cls._cached_voices:
            return cls._cached_voices

        try:
            raw_voices = await edge_tts.list_voices()
            enriched = []

            for v in raw_voices:
                short_name = v.get("ShortName", "")
                locale = v.get("Locale", "en-US")
                gender = v.get("Gender", "Neutral")
                friendly_name = v.get("FriendlyName", short_name)

                rec = RECOMMENDED_VOICES.get(short_name)
                is_recommended = rec is not None
                score = rec["score"] if rec else (50 if "Neural" in short_name else 30)
                display_name = rec["label"] if rec else f"{short_name} ({gender})"
                lang_display = LANGUAGE_NAMES.get(locale, locale)

                enriched.append({
                    "id": short_name,
                    "name": display_name,
                    "locale": locale,
                    "language": lang_display,
                    "gender": gender,
                    "is_recommended": is_recommended,
                    "score": score
                })

            # Sort: Recommended first, then by score, then by language
            enriched.sort(key=lambda x: (-x["is_recommended"], -x["score"], x["language"], x["name"]))
            cls._cached_voices = enriched
            return enriched
        except Exception as e:
            print(f"[WARN] Failed to fetch dynamic Edge-TTS voices: {e}")
            return cls._get_offline_fallback_voices()

    @classmethod
    def detect_best_voice(cls, script_text: str) -> str:
        """Auto-detects language and returns the best recommended voice."""
        text = script_text.strip()
        if not text:
            return "en-US-ChristopherNeural"

        # Check for Urdu / Arabic script
        if any('\u0600' <= c <= '\u06FF' for c in text):
            # Check for specific Urdu characters (ے, ٹ, ڈ, ڑ, ں)
            if any(c in "ٹڈڑںےہبھپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی" for c in text):
                return "ur-PK-AsadNeural"
            return "ar-SA-HamedNeural"

        # Check for Devanagari (Hindi)
        if any('\u0900' <= c <= '\u097F' for c in text):
            return "hi-IN-MadhurNeural"

        # Check for Japanese (Hiragana/Katakana/Kanji)
        if any('\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' for c in text):
            return "ja-JP-KeitaNeural"

        # Check for Cyrillic (Russian)
        if any('\u0400' <= c <= '\u04FF' for c in text):
            return "ru-RU-DmitryNeural"

        # Check for Chinese
        if any('\u4E00' <= c <= '\u9FFF' for c in text):
            return "zh-CN-YunxiNeural"

        # Default to English Viral Voice
        return "en-US-ChristopherNeural"

    @classmethod
    def _get_offline_fallback_voices(cls) -> List[Dict[str, Any]]:
        return [
            {"id": "en-US-ChristopherNeural", "name": "⭐ Christopher (Deep Storyteller)", "locale": "en-US", "language": "English (United States)", "gender": "Male", "is_recommended": True, "score": 99},
            {"id": "en-US-GuyNeural", "name": "⭐ Guy (Energetic / YouTube)", "locale": "en-US", "language": "English (United States)", "gender": "Male", "is_recommended": True, "score": 97},
            {"id": "en-US-JennyNeural", "name": "⭐ Jenny (Natural Female)", "locale": "en-US", "language": "English (United States)", "gender": "Female", "is_recommended": True, "score": 98},
            {"id": "en-GB-RyanNeural", "name": "⭐ Ryan (Cinematic British)", "locale": "en-GB", "language": "English (United Kingdom)", "gender": "Male", "is_recommended": True, "score": 99},
            {"id": "ur-PK-AsadNeural", "name": "⭐ Asad (Urdu Deep Voiceover)", "locale": "ur-PK", "language": "Urdu (Pakistan)", "gender": "Male", "is_recommended": True, "score": 99},
            {"id": "hi-IN-MadhurNeural", "name": "⭐ Madhur (Hindi Storyteller)", "locale": "hi-IN", "language": "Hindi (India)", "gender": "Male", "is_recommended": True, "score": 99}
        ]
