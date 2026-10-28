"""检查国内版官网 site/cn/（第 48 轮）。CI 测试里跑：先 build.py，再本脚本。

- 不该出现的词：学校用语（公司不能招生）、捐赠、境外服务、美元、绝对化用语（《广告法》）、美国版域名；
- 外部链接只允许备案系统（beian.miit.gov.cn、beian.mps.gov.cn）；
- 每页页脚有 ICP 备案号、公安备案号、生成式 AI 登记编号的模板位置；
- 页面引用的 /assets/ 文件都存在；Caddy 模板只用 env 和 regexFind。
有问题就列出并以非零状态退出。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site" / "cn"

BANNED = ["学院", "招生", "学费", "学分", "学位", "报名", "结业证书", "培训班", "职业技能培训", "捐赠", "不作为生意",
          "Claude", "Anthropic", "Google", "YouTube", "$", "美元", "世界一流", "最好", "最佳", "第一", "顶级", "首选",
          "wenquestrobotics", "Robotics Academy", "入驻"]
ALLOWED_HOSTS = {"beian.miit.gov.cn", "beian.mps.gov.cn"}
NEED = ['env "WQ_ICP"', 'env "WQ_PSB"', 'env "WQ_AI_REG"', 'env "WQ_COMPANY"']


def text_of(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"\{\{.*?\}\}", " ", t)
    return re.sub(r"<[^>]+>", " ", t)


def main():
    if not SITE.is_dir():
        print("site/cn 不存在：先运行 python3 tools/site_cn/build.py")
        return 1
    errs = []
    pages = sorted(SITE.rglob("*.html"))
    if len(pages) < 15:
        errs.append(f"页面太少：{len(pages)}")
    for p in pages:
        rel = p.relative_to(SITE)
        h = p.read_text(encoding="utf-8")
        t = text_of(h)
        for w in BANNED:
            if w in t or (w in ("Claude", "Anthropic", "Google", "YouTube", "wenquestrobotics") and w.lower() in h.lower()):
                errs.append(f"{rel}：出现“{w}”")
        for host in re.findall(r'(?:href|src)="https?://([^/"]+)', h):
            if host not in ALLOWED_HOSTS and not host.startswith("learn.{{"):
                errs.append(f"{rel}：外部链接 {host}")
        for k in NEED:
            if k not in h:
                errs.append(f"{rel}：页脚缺 {k}")
        for tpl in re.findall(r"\{\{(.*?)\}\}", h):
            words = re.findall(r"[A-Za-z_]+", tpl)
            if not set(words) <= {"with", "env", "else", "end", "regexFind", "WQ_ICP", "WQ_PSB", "WQ_AI_REG", "WQ_COMPANY",
                                  "WQ_CONTACT_PHONE", "WQ_CONTACT_EMAIL", "WQ_ADDRESS", "SITE_DOMAIN"}:
                errs.append(f"{rel}：未知的模板 {{{{{tpl}}}}}")
        for a in re.findall(r'"/assets/([^"?]+)', h):
            if not (SITE / "assets" / a).is_file():
                errs.append(f"{rel}：缺文件 /assets/{a}")
        if 'lang="zh-CN"' not in h:
            errs.append(f"{rel}：不是中文页面")
    js = (SITE / "assets" / "cn.js").read_text(encoding="utf-8") + (SITE / "assets" / "cn.css").read_text(encoding="utf-8")
    if "{{" in js:
        errs.append("cn.js / cn.css 里不能有 {{（会被当成模板）")
    for e in errs:
        print(e)
    print(f"国内版官网检查：{len(pages)} 页，{len(errs)} 个问题")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
