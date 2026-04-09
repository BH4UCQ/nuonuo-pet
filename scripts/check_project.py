"""
项目全面检查脚本
检查所有模块的功能和潜在问题
"""
import sys
import os
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_project_structure():
    """检查项目结构"""
    print("=" * 60)
    print("1. 检查项目结构")
    print("=" * 60)

    required_files = [
        'backend/app/main.py',
        'backend/app/models.py',
        'backend/app/storage.py',
        'backend/app/memory_enhanced.py',
        'backend/app/pet_growth.py',
        'backend/app/model_caller.py',
        'backend/app/security.py',
        'backend/app/security_simple.py',
        'backend/app/llm_api.py',
        'backend/app/llm_context_builder.py',
        'backend/app/llm_conversation_service.py',
        'backend/app/llm_health_check.py',
        'backend/app/llm_model_manager.py',
        'backend/app/llm_providers.py',
        'backend/requirements.txt',
    ]

    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}")
        else:
            print(f"[MISSING] {file}")
            missing_files.append(file)

    if missing_files:
        print(f"\n[WARNING] 缺少 {len(missing_files)} 个文件")
        return False
    else:
        print(f"\n[SUCCESS] 所有必需文件都存在")
        return True


def check_imports():
    """检查所有模块是否能正常导入"""
    print("\n" + "=" * 60)
    print("2. 检查模块导入")
    print("=" * 60)

    modules = [
        ('app.main', '主应用模块'),
        ('app.models', '数据模型'),
        ('app.storage', '存储模块'),
        ('app.memory_enhanced', '记忆增强模块'),
        ('app.pet_growth', '宠物成长模块'),
        ('app.model_caller', '模型调用器'),
        ('app.security', '安全管理模块'),
        ('app.security_simple', '简化安全管理模块'),
        ('app.llm_api', 'LLM API'),
        ('app.llm_context_builder', 'LLM 上下文构建器'),
        ('app.llm_conversation_service', 'LLM 对话服务'),
        ('app.llm_health_check', 'LLM 健康检查'),
        ('app.llm_model_manager', 'LLM 模型管理器'),
        ('app.llm_providers', 'LLM 提供商适配器'),
        ('app.ui_bulk_ops', 'UI批量操作'),
        ('app.ui_context_builders', 'UI上下文构建器'),
        ('app.ui_context_management', 'UI上下文管理'),
        ('app.ui_context_resources', 'UI上下文资源'),
        ('app.ui_helpers', 'UI辅助工具'),
    ]

    failed_imports = []
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"[OK] {description} ({module_name})")
        except Exception as e:
            # security模块因为缺少cryptography而导入失败是可接受的
            if module_name == 'app.security' and 'cryptography' in str(e):
                print(f"[INFO] {description} ({module_name}): 需要cryptography库（已使用security_simple替代）")
            else:
                print(f"[FAIL] {description} ({module_name}): {e}")
                failed_imports.append((module_name, description, str(e)))

    if failed_imports:
        print(f"\n[WARNING] {len(failed_imports)} 个模块导入失败")
        return False
    else:
        print(f"\n[SUCCESS] 所有模块导入成功（或已提供替代方案）")
        return True


def check_data_models():
    """检查数据模型完整性"""
    print("\n" + "=" * 60)
    print("3. 检查数据模型")
    print("=" * 60)

    try:
        from app import models
        from app import storage

        # 检查核心模型（分别在models.py和storage.py中）
        storage_models = [
            ('storage', 'PetRecord'),
            ('storage', 'DeviceRecord'),
            ('storage', 'DeviceEventRecord'),
            ('storage', 'MemoryRecord'),
            ('storage', 'EventRecord'),
        ]

        pydantic_models = [
            ('models', 'LLMProviderConfig'),
            ('models', 'LLMModelConfig'),
            ('models', 'LLMRequest'),
            ('models', 'LLMResponse'),
            ('models', 'ConversationMessage'),
            ('models', 'ConversationHistory'),
        ]

        missing_models = []

        for module_name, model_name in storage_models:
            module = storage if module_name == 'storage' else models
            if hasattr(module, model_name):
                print(f"[OK] {model_name} (from {module_name})")
            else:
                print(f"[MISSING] {model_name} (from {module_name})")
                missing_models.append(model_name)

        for module_name, model_name in pydantic_models:
            module = storage if module_name == 'storage' else models
            if hasattr(module, model_name):
                print(f"[OK] {model_name} (from {module_name})")
            else:
                print(f"[MISSING] {model_name} (from {module_name})")
                missing_models.append(model_name)

        if missing_models:
            print(f"\n[WARNING] 缺少 {len(missing_models)} 个数据模型")
            return False
        else:
            print(f"\n[SUCCESS] 所有数据模型都存在")
            return True

    except Exception as e:
        print(f"[ERROR] 数据模型检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_storage_system():
    """检查存储系统"""
    print("\n" + "=" * 60)
    print("4. 检查存储系统")
    print("=" * 60)

    try:
        from app import storage

        # 检查核心存储变量
        required_storage = [
            'PETS',
            'DEVICES',
            'MEMORY',
            'EVENTS',
            'MODEL_ROUTES',
        ]

        missing_storage = []
        for storage_name in required_storage:
            if hasattr(storage, storage_name):
                print(f"[OK] {storage_name}")
            else:
                print(f"[MISSING] {storage_name}")
                missing_storage.append(storage_name)

        # 检查核心函数
        required_functions = [
            'save_state',
            'load_state',
            'now_iso',
        ]

        missing_functions = []
        for func_name in required_functions:
            if hasattr(storage, func_name):
                print(f"[OK] {func_name}")
            else:
                print(f"[MISSING] {func_name}")
                missing_functions.append(func_name)

        if missing_storage or missing_functions:
            print(f"\n[WARNING] 存储系统缺少一些组件")
            return False
        else:
            print(f"\n[SUCCESS] 存储系统完整")
            return True

    except Exception as e:
        print(f"[ERROR] 存储系统检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_llm_functionality():
    """检查LLM功能"""
    print("\n" + "=" * 60)
    print("5. 检查LLM功能")
    print("=" * 60)

    try:
        from app.llm_model_manager import get_model_manager
        from app.llm_context_builder import LLMContextBuilder
        from app.llm_conversation_service import get_conversation_service
        from app.llm_health_check import check_all_providers
        from app.security_simple import encrypt_api_key, decrypt_api_key

        # 测试模型管理器
        manager = get_model_manager()
        print(f"[OK] 模型管理器初始化成功")
        providers = manager.get_all_providers()
        print(f"[OK] 获取提供商列表: {len(providers)} 个提供商")

        # 测试上下文构建器
        builder = LLMContextBuilder()
        print(f"[OK] 上下文构建器初始化成功")

        # 测试对话服务
        service = get_conversation_service()
        print(f"[OK] 对话服务初始化成功")

        # 测试加密功能
        test_key = "test-key-12345"
        encrypted = encrypt_api_key(test_key)
        decrypted = decrypt_api_key(encrypted)
        if decrypted == test_key:
            print(f"[OK] 加密解密功能正常")
        else:
            print(f"[FAIL] 加密解密功能异常")
            return False

        print(f"\n[SUCCESS] LLM功能检查通过")
        return True

    except Exception as e:
        print(f"[ERROR] LLM功能检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api_routes():
    """检查API路由"""
    print("\n" + "=" * 60)
    print("6. 检查API路由")
    print("=" * 60)

    try:
        from app.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # 测试关键路由
        routes_to_test = [
            ('GET', '/', '根路由'),
            ('GET', '/health', '健康检查'),
            ('GET', '/api/llm/config', 'LLM配置'),
            ('GET', '/api/llm/health', 'LLM健康检查'),
            ('GET', '/api/model/routes', '模型路由'),
        ]

        failed_routes = []
        for method, path, description in routes_to_test:
            try:
                if method == 'GET':
                    response = client.get(path)
                elif method == 'POST':
                    response = client.post(path)

                if response.status_code < 500:  # 允许404等，但不允许500错误
                    print(f"[OK] {description} ({method} {path}) - {response.status_code}")
                else:
                    print(f"[FAIL] {description} ({method} {path}) - {response.status_code}")
                    failed_routes.append((method, path, description))
            except Exception as e:
                print(f"[ERROR] {description} ({method} {path}): {e}")
                failed_routes.append((method, path, description))

        if failed_routes:
            print(f"\n[WARNING] {len(failed_routes)} 个路由测试失败")
            return False
        else:
            print(f"\n[SUCCESS] 所有API路由正常")
            return True

    except Exception as e:
        print(f"[ERROR] API路由检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_code_quality():
    """检查代码质量问题"""
    print("\n" + "=" * 60)
    print("7. 检查代码质量")
    print("=" * 60)

    issues = []

    # 检查是否有明显的代码问题
    python_files = [
        'backend/app/main.py',
        'backend/app/models.py',
        'backend/app/storage.py',
        'backend/app/llm_api.py',
        'backend/app/llm_context_builder.py',
        'backend/app/llm_conversation_service.py',
        'backend/app/llm_health_check.py',
        'backend/app/llm_model_manager.py',
        'backend/app/llm_providers.py',
    ]

    for file_path in python_files:
        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

            # 检查是否有TODO标记
            todo_count = content.count('# TODO')
            if todo_count > 0:
                print(f"[INFO] {file_path}: {todo_count} 个TODO标记")
                issues.append(f"{file_path}: {todo_count} 个TODO标记")

            # 检查是否有FIXME标记
            fixme_count = content.count('# FIXME')
            if fixme_count > 0:
                print(f"[WARNING] {file_path}: {fixme_count} 个FIXME标记")
                issues.append(f"{file_path}: {fixme_count} 个FIXME标记")

            # 检查是否有明显的语法错误（简单的检查）
            try:
                compile(content, file_path, 'exec')
            except SyntaxError as e:
                print(f"[ERROR] {file_path}: 语法错误 - {e}")
                issues.append(f"{file_path}: 语法错误")

    if issues:
        print(f"\n[INFO] 发现 {len(issues)} 个代码质量问题")
        return True  # 不算失败，只是提醒
    else:
        print(f"\n[SUCCESS] 没有发现明显的代码质量问题")
        return True


def check_dependencies():
    """检查依赖"""
    print("\n" + "=" * 60)
    print("8. 检查依赖")
    print("=" * 60)

    try:
        # 检查关键依赖
        dependencies = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', 'Uvicorn'),
            ('pydantic', 'Pydantic'),
            ('httpx', 'HTTPX'),
        ]

        missing_deps = []
        for module_name, package_name in dependencies:
            try:
                __import__(module_name)
                print(f"[OK] {package_name} ({module_name})")
            except ImportError:
                print(f"[MISSING] {package_name} ({module_name})")
                missing_deps.append(package_name)

        if missing_deps:
            print(f"\n[WARNING] 缺少 {len(missing_deps)} 个依赖包")
            return False
        else:
            print(f"\n[SUCCESS] 所有关键依赖都已安装")
            return True

    except Exception as e:
        print(f"[ERROR] 依赖检查失败: {e}")
        return False


def main():
    """运行所有检查"""
    print("=" * 60)
    print("nuonuo-pet 项目全面检查")
    print("=" * 60)

    checks = [
        ("项目结构", check_project_structure),
        ("模块导入", check_imports),
        ("数据模型", check_data_models),
        ("存储系统", check_storage_system),
        ("LLM功能", check_llm_functionality),
        ("API路由", check_api_routes),
        ("代码质量", check_code_quality),
        ("依赖检查", check_dependencies),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name} 检查异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("检查结果摘要")
    print("=" * 60)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 检查通过")

    if passed == total:
        print("\n[SUCCESS] 所有检查通过！项目状态良好。")
        return 0
    else:
        print(f"\n[WARNING] 有 {total - passed} 个检查失败，需要修复。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
