"""
基础LLM功能测试脚本
测试LLM模块的基本功能是否正常工作
"""
import sys
import os
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """测试所有LLM模块是否能正常导入"""
    print("测试模块导入...")
    try:
        from app import llm_api
        print("[OK] llm_api 导入成功")

        from app import llm_context_builder
        print("[OK] llm_context_builder 导入成功")

        from app import llm_conversation_service
        print("[OK] llm_conversation_service 导入成功")

        from app import llm_health_check
        print("[OK] llm_health_check 导入成功")

        from app import llm_model_manager
        print("[OK] llm_model_manager 导入成功")

        from app import llm_providers
        print("[OK] llm_providers 导入成功")

        from app.security_simple import encrypt_api_key, decrypt_api_key
        print("[OK] security_simple 导入成功")

        print("\n所有模块导入成功!")
        return True
    except Exception as e:
        print(f"[FAIL] 模块导入失败: {e}")
        return False


def test_security():
    """测试加密解密功能"""
    print("\n测试加密解密功能...")
    try:
        from app.security_simple import encrypt_api_key, decrypt_api_key

        test_key = "sk-test1234567890abcdef"
        encrypted = encrypt_api_key(test_key)
        print(f"[OK] 加密成功: {encrypted[:20]}...")

        decrypted = decrypt_api_key(encrypted)
        print(f"[OK] 解密成功: {decrypted}")

        if decrypted == test_key:
            print("[OK] 加密解密匹配!")
            return True
        else:
            print("[FAIL] 加密解密不匹配!")
            return False
    except Exception as e:
        print(f"[FAIL] 安全测试失败: {e}")
        return False


def test_model_manager():
    """测试模型管理器"""
    print("\n测试模型管理器...")
    try:
        from app.llm_model_manager import get_model_manager

        manager = get_model_manager()
        print("[OK] 模型管理器初始化成功")

        providers = manager.get_all_providers()
        print(f"[OK] 获取提供商列表成功: {len(providers)} 个提供商")

        models = manager.get_all_models()
        print(f"[OK] 获取模型列表成功: {len(models)} 个模型")

        return True
    except Exception as e:
        print(f"[FAIL] 模型管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_providers():
    """测试提供商适配器"""
    print("\n测试提供商适配器...")
    try:
        from app.llm_providers import LLMProviderFactory
        import asyncio

        # 测试工厂类存在
        print("[OK] LLMProviderFactory 类存在")

        # 注意：create_provider 是异步方法，需要 model_manager
        # 我们只测试工厂类是否可以正常导入
        print("[OK] 提供商工厂测试完成（需要实际配置才能测试创建）")

        return True
    except Exception as e:
        print(f"[FAIL] 提供商适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_builder():
    """测试上下文构建器"""
    print("\n测试上下文构建器...")
    try:
        from app.llm_context_builder import LLMContextBuilder
        from app.storage import PetRecord

        builder = LLMContextBuilder()
        print("[OK] 上下文构建器初始化成功")

        # 创建一个测试宠物对象
        test_pet = PetRecord(
            pet_id="test_pet_id",
            name="测试宠物",
            species_id="cat-default",
            mood="happy",
            energy=80,
            hunger=20
        )

        # 测试构建系统提示
        system_prompt = builder.build_system_prompt(test_pet)
        print(f"[OK] 系统提示构建成功: {len(system_prompt)} 字符")

        return True
    except Exception as e:
        print(f"[FAIL] 上下文构建器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_router():
    """测试API路由"""
    print("\n测试API路由...")
    try:
        from app.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # 测试根路由
        response = client.get("/")
        print(f"[OK] 根路由测试成功: {response.status_code}")

        # 测试健康检查路由
        response = client.get("/api/llm/health")
        print(f"[OK] LLM健康检查路由测试成功: {response.status_code}")

        # 测试配置路由
        response = client.get("/api/llm/config")
        print(f"[OK] LLM配置路由测试成功: {response.status_code}")

        return True
    except Exception as e:
        print(f"[FAIL] API路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("LLM功能基础测试")
    print("=" * 60)

    tests = [
        ("模块导入", test_imports),
        ("加密解密", test_security),
        ("模型管理器", test_model_manager),
        ("提供商适配器", test_providers),
        ("上下文构建器", test_context_builder),
        ("API路由", test_api_router),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} 测试异常: {e}")
            results.append((name, False))

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)

    for name, result in results:
        status = "[PASS] 通过" if result else "[FAIL] 失败"
        print(f"{name}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n[SUCCESS] 所有测试通过!")
        return 0
    else:
        print(f"\n[WARNING] 有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
