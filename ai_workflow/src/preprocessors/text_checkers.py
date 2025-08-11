import re
import langid
from langdetect import detect_langs, DetectorFactory, LangDetectException

DetectorFactory.seed = 0  # For consistent langdetect results

class ArabicLanguageDetector:
    def __init__(self, thresholds=None):
        self.thresholds = thresholds or {
            "manual": 0.95,
            "langdetect": 0.95
        }

    def is_arabic_manual(self, text):
        arabic_ranges = [
            (0x0600, 0x06FF), (0x0750, 0x077F),
            (0x08A0, 0x08FF), (0xFB50, 0xFDFF),
            (0xFE70, 0xFEFF)
        ]
        arabic_count = 0
        total_letters = 0

        for char in text:
            if char.isalpha():
                total_letters += 1
                code = ord(char)
                if any(start <= code <= end for start, end in arabic_ranges):
                    arabic_count += 1

        if total_letters == 0:
            return False, 0.0

        percent = arabic_count / total_letters
        return percent >= self.thresholds["manual"], percent * 100

    def is_arabic_langid(self, text):
        lang, score = langid.classify(text)
        return (lang == 'ar'), lang

    def is_arabic_langdetect(self, text):
        try:
            langs = detect_langs(text)
            if not langs:
                return False, None, None
            top = langs[0]
            return (top.lang == 'ar' and top.prob >= self.thresholds["langdetect"]), top.lang, top.prob
        except LangDetectException:
            return False, None, None
        except Exception as e:
            print(f"[langdetect] Error: {e}")
            return False, None, None

    def check_text(self, text: str, debug=False) -> bool:
        is_ar_manual, percent = self.is_arabic_manual(text)
        is_ar_langid, langid_code = self.is_arabic_langid(text)
        is_ar_ld, ld_code, ld_prob = self.is_arabic_langdetect(text)

        if debug:
            print(f"[Manual] Is Arabic: {is_ar_manual} | Percent: {percent:.2f}%")
            print(f"[LangID] Is Arabic: {is_ar_langid} | Lang: {langid_code}")
            print(f"[LangDetect] Is Arabic: {is_ar_ld} | Lang: {ld_code} | Prob: {ld_prob:.4f}")

        votes = sum([
            is_ar_manual,
            is_ar_langid,
            is_ar_ld
        ])
        return votes >= 2  # Majority voting


