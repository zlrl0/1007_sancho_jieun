from paperqa import Settings

s = Settings.from_name("wikicrow")
print(s.answer.evidence_k, s.answer.answer_max_sources)