"""第 34 轮：国内部署（WQ_REGION=cn）只用已备案模型；不写地区时行为不变。"""
from app.ai import ModelGateway
from app.config import Settings, model_choice


def gateway(**kw):
    provider, key = model_choice(Settings(**kw))
    return ModelGateway(provider, None, anthropic_key=key, deepseek_key=kw.get("deepseek_api_key", ""))


def test_default_region_unchanged():
    assert Settings().region == "us"
    assert gateway(anthropic_api_key="sk-ant", deepseek_api_key="ds").provider == "claude"
    assert gateway(deepseek_api_key="ds").provider == "deepseek"


def test_cn_ignores_claude_key():
    assert gateway(region="cn", anthropic_api_key="sk-ant", deepseek_api_key="ds").provider == "deepseek"
    assert gateway(region="CN", anthropic_api_key="sk-ant").provider == "none"
    assert gateway(region="cn", ai_provider="claude", anthropic_api_key="sk-ant", deepseek_api_key="ds").provider == "deepseek"
    assert model_choice(Settings(region="cn", anthropic_api_key="sk-ant"))[1] == ""

