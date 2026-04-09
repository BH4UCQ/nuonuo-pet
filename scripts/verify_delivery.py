"""
可交付包验证脚本
验证 nuonuo-pet-deliverable 文件夹的完整性和可用性
"""
import sys
import os
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def verify_delivery():
    """验证可交付包的完整性"""
    print("=" * 60)
    print("nuonuo-pet 可交付包验证")
    print("=" * 60)

    # 必需的文件和目录
    required_items = {
        '根目录文件': [
            'README.md',
            'LICENSE',
            'CHANGELOG.md',
            'CONTRIBUTING.md',
            '.gitignore',
            'setup.bat',
            'setup.sh',
            'start.bat',
            'start.sh',
            'PROJECT_MANIFEST.md',
        ],
        'backend目录': [
            'backend/requirements.txt',
            'backend/app/__init__.py',
            'backend/app/main.py',
            'backend/app/models.py',
            'backend/app/storage.py',
        ],
        'LLM模块': [
            'backend/app/llm_api.py',
            'backend/app/llm_context_builder.py',
            'backend/app/llm_conversation_service.py',
            'backend/app/llm_health_check.py',
            'backend/app/llm_model_manager.py',
            'backend/app/llm_providers.py',
        ],
        '安全模块': [
            'backend/app/security.py',
            'backend/app/security_simple.py',
        ],
        '文档目录': [
            'docs/LLM_RECOVERY_SUMMARY.md',
            'docs/PROJECT_STATUS_REPORT.md',
            'docs/DEPLOYMENT.md',
        ],
        '脚本目录': [
            'scripts/check_project.py',
        ],
        '测试目录': [
            'backend/tests/test_llm_basic.py',
        ],
    }

    missing_items = []
    total_items = 0
    found_items = 0

    for category, items in required_items.items():
        print(f"\n检查 {category}:")
        for item in items:
            total_items += 1
            if os.path.exists(item):
                print(f"  [OK] {item}")
                found_items += 1
            else:
                print(f"  [MISSING] {item}")
                missing_items.append(item)

    # 验证Python文件语法
    print("\n" + "=" * 60)
    print("验证 Python 文件语法")
    print("=" * 60)

    python_files = []
    for root, dirs, files in os.walk('backend/app'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
            print(f"[OK] {py_file}")
        except SyntaxError as e:
            print(f"[ERROR] {py_file}: {e}")
            syntax_errors.append((py_file, str(e)))

    # 验证文档文件
    print("\n" + "=" * 60)
    print("验证文档文件")
    print("=" * 60)

    doc_files = [
        'README.md',
        'LICENSE',
        'CHANGELOG.md',
        'CONTRIBUTING.md',
        'PROJECT_MANIFEST.md',
        'docs/LLM_RECOVERY_SUMMARY.md',
        'docs/PROJECT_STATUS_REPORT.md',
        'docs/DEPLOYMENT.md',
    ]

    for doc_file in doc_files:
        if os.path.exists(doc_file):
            size = os.path.getsize(doc_file)
            print(f"[OK] {doc_file} ({size} bytes)")
        else:
            print(f"[MISSING] {doc_file}")
            missing_items.append(doc_file)

    # 验证脚本文件
    print("\n" + "=" * 60)
    print("验证脚本文件")
    print("=" * 60)

    script_files = [
        'setup.bat',
        'setup.sh',
        'start.bat',
        'start.sh',
        'scripts/check_project.py',
    ]

    for script_file in script_files:
        if os.path.exists(script_file):
            size = os.path.getsize(script_file)
            print(f"[OK] {script_file} ({size} bytes)")
        else:
            print(f"[MISSING] {script_file}")
            missing_items.append(script_file)

    # 输出验证结果
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)

    print(f"文件完整性: {found_items}/{total_items} ({found_items*100//total_items}%)")
    print(f"Python 语法错误: {len(syntax_errors)}")
    print(f"缺失文件: {len(missing_items)}")

    if missing_items:
        print("\n缺失的文件:")
        for item in missing_items:
            print(f"  - {item}")

    if syntax_errors:
        print("\n语法错误:")
        for file, error in syntax_errors:
            print(f"  - {file}: {error}")

    # 最终判断
    print("\n" + "=" * 60)
    if not missing_items and not syntax_errors:
        print("[SUCCESS] 可交付包验证通过！")
        print("\n可以安全地上传到 GitHub 或部署到生产环境。")
        return 0
    else:
        print("[WARNING] 可交付包存在问题，请修复后再使用。")
        return 1

if __name__ == "__main__":
    sys.exit(verify_delivery())
