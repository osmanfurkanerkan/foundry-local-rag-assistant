from rag_engine.interfaces.models import ConversationTurn
from rag_engine.pipeline.prompt_builder import NOT_FOUND_MESSAGE, build_prompt, is_refusal
from tests.conftest import make_chunk


def test_build_prompt_includes_context_and_question():
    prompt = build_prompt("Soru?", [make_chunk("doc-a", "Onemli bilgi.")])

    assert "Soru?" in prompt
    assert "Onemli bilgi." in prompt
    assert "[doc-a]" in prompt


def test_build_prompt_without_history_has_no_history_block():
    prompt = build_prompt("Soru?", [make_chunk("doc-a")])

    assert "CONVERSATION HISTORY" not in prompt


def test_build_prompt_with_history_includes_previous_turn():
    history = [ConversationTurn(question="Onceki soru", answer="Onceki cevap")]
    prompt = build_prompt("Soru?", [make_chunk("doc-a")], history)

    assert "CONVERSATION HISTORY" in prompt
    assert "Onceki soru" in prompt
    assert "Onceki cevap" in prompt


def test_not_found_message_is_present_in_system_instruction():
    prompt = build_prompt("Soru?", [make_chunk("doc-a")])

    assert NOT_FOUND_MESSAGE in prompt


def test_is_refusal_true_when_answer_starts_with_message():
    assert is_refusal(f"  {NOT_FOUND_MESSAGE}")


def test_is_refusal_false_when_message_only_trails_a_real_answer():
    # Faz 7.3'te canli provada bulunan gercek bug: kucuk model bazen dogru
    # bir cevabin sonuna bu ifadeyi ekliyor -- bu, gecerli bir cevap olarak
    # sayilmali (kaynaklar gizlenmemeli).
    assert not is_refusal(f"Gecerli bir cevap burada. {NOT_FOUND_MESSAGE}")
