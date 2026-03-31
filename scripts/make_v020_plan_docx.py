from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path

out = Path('/home/bh4ucq/.nanobot/workspace/nuonuo-pet/v0.2.0_plan.docx')

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
    <w:rPr><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>
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
    p('nuonuo-pet v0.2.0 开发计划', 'Heading1'),
    p('状态：规划中 ｜ 目标：从“跑通闭环”走向“产品化增强”'),
    p('目标定位', 'Heading2'),
    p('v0.1.0 已完成基础收口，v0.2.0 的重点不是再做“骨架”，而是把可配置能力真正做深。'),
    bullet('让模型提供方可切换、可降级、可按成本/速度路由'),
    bullet('让记忆从“有接口”升级为“可持久、可分层、可检索”'),
    bullet('让主题和资源从“可预览”升级为“可导入、可校验、可回滚”'),
    bullet('让设备端从“能跑”升级为“能识别能力、自动选模板、稳定恢复”'),
    bullet('让宠物成长从“状态字段”升级为“有节奏、有事件、有偏好演化”'),
    p('核心方向', 'Heading2'),
    bullet('记忆系统正式化：短期 / 长期 / 事件分层，支持来源、置信度与检索'),
    bullet('模型路由可配置化：默认、备用、失败回退与路由解释'),
    bullet('资源包与主题包流程完善：导入、校验、预览、启用、回滚'),
    bullet('设备端稳定性增强：离线、恢复、低电量、错误恢复路径'),
    bullet('宠物成长与事件系统增强：偏好形成、物种曲线、事件细化'),
    p('建议优先级', 'Heading2'),
    bullet('P0：记忆持久化、模型路由配置、chat 返回路由解释'),
    bullet('P1：资源包导入/启用/回滚、主题版本与兼容校验、设备能力摘要增强'),
    bullet('P2：成长偏好演化、事件系统细化、多设备同步雏形'),
    p('完成标准', 'Heading2'),
    bullet('宠物记忆能保存并复用'),
    bullet('模型可切换并可降级'),
    bullet('资源包可导入并可回滚'),
    bullet('设备能稳定恢复并自动拉起宠物摘要'),
    bullet('宠物的成长、情绪和偏好有连续变化'),
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
