from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

out = Path('/home/bh4ucq/.nanobot/workspace/nuonuo-pet/release_notes_v0.1.0.docx')

content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''

rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="R1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'''

styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="28"/></w:rPr>
  </w:style>
</w:styles>'''

def esc(text: str) -> str:
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def p(text, style=None):
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'

def bullet(text):
    return f'<w:p><w:pPr><w:pStyle w:val="Normal"/><w:ind w:left="720"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t xml:space="preserve">• {esc(text)}</w:t></w:r></w:p>'

paras = [
    p('nuonuo-pet v0.1.0 发布说明', 'Heading1'),
    p('状态：已完成收口 ｜ 目标：M0-M4 全部完成'),
    p('版本概述', 'Heading2'),
    p('nuonuo-pet 是一个可配置、可成长、可多形态的 AI 电子宠物项目。v0.1.0 完成了从仓库骨架、后端接口、宠物核心、资源与主题、绑定与恢复，到 ESP32 固件可编译的完整基础闭环。'),
    p('本版本完成内容', 'Heading2'),
    bullet('仓库骨架、愿景、路线图、交互流程和开发顺序已明确'),
    bullet('FastAPI 后端已具备设备注册、绑定、状态同步、记忆、宠物、模型路由和资源接口'),
    bullet('宠物核心已包含成长阶段、情绪、事件驱动变化、记忆摘要与成长摘要'),
    bullet('物种模板、主题包、资源槽位、预览和设备能力分级已接通'),
    bullet('设备离线、恢复、心跳、事件留痕与宠物-设备关联已完成'),
    bullet('ESP32 固件状态机已可编译，PlatformIO 编译链路已验证'),
    bullet('绑定流程、自检脚本、最简日志约定和发布准备说明已补齐'),
    p('关键接口与能力', 'Heading2'),
    bullet('设备注册 / 绑定 / 心跳 / 状态'),
    bullet('宠物创建 / 更新 / 事件 / 记忆 / 成长摘要'),
    bullet('物种模板 / 模型路由 / 主题验证 / 资源验证'),
    bullet('预览接口、设备能力分级、display_hint 推荐'),
    bullet('设备事件日志、健康查询、恢复同步'),
    p('构建验证', 'Heading2'),
    p('已在仓库内虚拟环境 .venv_pio 中安装 PlatformIO，并成功执行：'),
    p('pio run -d firmware/esp32'),
    p('结果显示 ESP32-S3 固件编译成功。'),
    p('版本结论', 'Heading2'),
    p('nuonuo-pet v0.1.0 已按开发计划完成收口。当前仓库状态可以作为基础版本交付和后续迭代起点。'),
]

document = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n' \
           '  <w:body>\n    ' + '\n    '.join(paras) + '\n' \
           '    <w:sectPr>\n' \
           '      <w:pgSz w:w="11906" w:h="16838"/>\n' \
           '      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>\n' \
           '    </w:sectPr>\n' \
           '  </w:body>\n' \
           '</w:document>'

with ZipFile(out, 'w', ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels)
    z.writestr('word/document.xml', document)
    z.writestr('word/_rels/document.xml.rels', doc_rels)
    z.writestr('word/styles.xml', styles)
print(out)
