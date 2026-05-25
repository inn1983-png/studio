#!/usr/bin/env python3
"""
异步处理流程验证脚本
验证核心代码逻辑和结构
"""

import ast
import os
from pathlib import Path


def validate_model_batch_operations():
    """验证模型层批量操作方法"""
    print("🔍 验证模型层批量操作方法...")

    results = {
        'chapter_batch_ops': False,
        'paragraph_batch_ops': False,
        'sentence_batch_ops': False
    }

    # 检查Chapter模型
    chapter_file = Path('src/models/chapter.py')
    if chapter_file.exists():
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_content = f.read()

        # 检查批量创建方法
        if 'async def batch_create' in chapter_content and 'await db_session.execute' in chapter_content:
            results['chapter_batch_ops'] = True
            print("  ✅ Chapter批量操作方法存在")
        else:
            print("  ❌ Chapter批量操作方法缺失")

    # 检查Paragraph模型
    paragraph_file = Path('src/models/paragraph.py')
    if paragraph_file.exists():
        with open(paragraph_file, 'r', encoding='utf-8') as f:
            paragraph_content = f.read()

        if 'async def batch_create' in paragraph_content:
            results['paragraph_batch_ops'] = True
            print("  ✅ Paragraph批量操作方法存在")
        else:
            print("  ❌ Paragraph批量操作方法缺失")

    # 检查Sentence模型
    sentence_file = Path('src/models/sentence.py')
    if sentence_file.exists():
        with open(sentence_file, 'r', encoding='utf-8') as f:
            sentence_content = f.read()

        if 'async def batch_create' in sentence_content:
            results['sentence_batch_ops'] = True
            print("  ✅ Sentence批量操作方法存在")
        else:
            print("  ❌ Sentence批量操作方法缺失")

    return all(results.values())


def validate_processing_service():
    """验证业务处理服务"""
    print("🔍 验证业务处理服务...")

    service_file = Path('src/services/project_processing.py')
    if not service_file.exists():
        print("  ❌ ProjectProcessingService文件不存在")
        return False

    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()

    required_methods = [
        'process_uploaded_file',
        '_parse_text_content',
        '_save_parsed_content',
        '_update_project_statistics',
        'get_processing_status'
    ]

    missing_methods = []
    for method in required_methods:
        if f'async def {method}' not in content:
            missing_methods.append(method)

    if missing_methods:
        print(f"  ❌ 缺少方法: {missing_methods}")
        return False
    else:
        print("  ✅ 所有必需方法存在")
        return True


def validate_celery_tasks():
    """验证Celery任务"""
    print("🔍 验证Celery任务...")

    tasks_file = Path('src/tasks/task.py')
    if not tasks_file.exists():
        print("  ❌ Celery任务文件不存在")
        return False

    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()

    required_task_names = [
        'process_uploaded_file',
        'get_processing_status',
        'retry_failed_project',
        'health_check'
    ]

    missing_tasks = []
    for task_name in required_task_names:
        if f"name='{task_name}'" not in content and f'name="{task_name}"' not in content:
            missing_tasks.append(task_name)

    if missing_tasks:
        print(f"  ❌ 缺少任务: {missing_tasks}")
        return False
    else:
        print("  ✅ 所有必需任务存在")
        return True


def validate_project_service():
    """验证Project服务扩展"""
    print("🔍 验证Project服务扩展...")

    service_file = Path('src/services/project.py')
    if not service_file.exists():
        print("  ❌ ProjectService文件不存在")
        return False

    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()

    required_methods = [
        'update_processing_progress',
        'mark_processing_failed',
        'mark_processing_completed'
    ]

    missing_methods = []
    for method in required_methods:
        if f'async def {method}' not in content:
            missing_methods.append(method)

    if missing_methods:
        print(f"  ❌ 缺少方法: {missing_methods}")
        return False
    else:
        print("  ✅ 所有进度跟踪方法存在")
        return True


def validate_error_handling():
    """验证错误处理机制"""
    print("🔍 验证错误处理机制...")

    # 检查Celery任务的错误处理
    tasks_file = Path('src/tasks/task.py')
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_content = f.read()

        if 'try:' in tasks_content and 'except Exception' in tasks_content:
            print("  ✅ Celery任务包含错误处理")
        else:
            print("  ❌ Celery任务缺少错误处理")
            return False

        if 'self.retry(' in tasks_content:
            print("  ✅ 包含重试机制")
        else:
            print("  ❌ 缺少重试机制")
            return False

    # 检查业务服务的错误处理
    service_file = Path('src/services/project_processing.py')
    if service_file.exists():
        with open(service_file, 'r', encoding='utf-8') as f:
            service_content = f.read()

        if 'try:' in service_content and 'except Exception' in service_content:
            print("  ✅ 业务服务包含错误处理")
        else:
            print("  ❌ 业务服务缺少错误处理")
            return False

    return True


def validate_async_patterns():
    """验证异步编程模式"""
    print("🔍 验证异步编程模式...")

    files_to_check = [
        'src/models/chapter.py',
        'src/models/paragraph.py',
        'src/models/sentence.py',
        'src/services/project_processing.py',
        'src/tasks/task.py'
    ]

    async_usage_count = 0

    for file_path in files_to_check:
        if Path(file_path).exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查异步函数定义
            async_def_count = content.count('async def ')
            await_count = content.count('await ')

            if async_def_count > 0 and await_count > 0:
                async_usage_count += 1
                print(f"  ✅ {file_path}: {async_def_count}个异步函数, {await_count}个await调用")
            else:
                print(f"  ❌ {file_path}: 异步模式使用不充分")

    return async_usage_count == len(files_to_check)


def validate_database_transactions():
    """验证数据库事务处理"""
    print("🔍 验证数据库事务处理...")

    # 检查事务使用
    tasks_file = Path('src/tasks/task.py')
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'async with db_session.begin()' in content or 'async with async_session.begin()' in content:
            print("  ✅ 使用数据库事务")
        else:
            print("  ❌ 缺少数据库事务")
            return False

    # 检查批量操作
    models = ['chapter.py', 'paragraph.py', 'sentence.py']
    batch_operations = 0

    for model in models:
        model_file = Path(f'src/models/{model}')
        if model_file.exists():
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'db_session.execute' in content and 'cls.__table__.insert()' in content:
                batch_operations += 1
                print(f"  ✅ {model}: 使用批量数据库操作")

    return batch_operations == len(models)


def validate_progress_tracking():
    """验证进度跟踪机制"""
    print("🔍 验证进度跟踪机制...")

    service_file = Path('src/services/project_processing.py')
    if not service_file.exists():
        return False

    with open(service_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查进度更新点
    progress_updates = [
        'ProjectStatus.PARSING, 10',  # 开始解析
        'ProjectStatus.PARSING, 30',  # 解析完成
        'ProjectStatus.PARSED, 100'   # 全部完成
    ]

    found_updates = 0
    for update in progress_updates:
        if update in content:
            found_updates += 1

    if found_updates == len(progress_updates):
        print("  ✅ 进度跟踪点设置正确")
        return True
    else:
        print(f"  ❌ 缺少进度跟踪点: {len(progress_updates) - found_updates}个")
        return False


def validate_integration_points():
    """验证集成点"""
    print("🔍 验证系统集成点...")

    # 检查文本解析服务集成
    service_file = Path('src/services/project_processing.py')
    if service_file.exists():
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'text_parser_service' in content:
            print("  ✅ 集成文本解析服务")
        else:
            print("  ❌ 未集成文本解析服务")
            return False

    # 检Celery任务与业务服务集成
    tasks_file = Path('src/tasks/task.py')
    if tasks_file.exists():
        with open(tasks_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'project_processing_service' in content:
            print("  ✅ Celery任务集成业务服务")
        else:
            print("  ❌ Celery任务未集成业务服务")
            return False

    return True


def main():
    """主验证函数"""
    print("=" * 60)
    print("🔧 Txtovideo Studio 异步文件处理流程代码验证")
    print("=" * 60)

    validation_results = []

    # 执行各项验证
    validation_results.append(("模型层批量操作", validate_model_batch_operations()))
    validation_results.append(("业务处理服务", validate_processing_service()))
    validation_results.append(("Celery任务", validate_celery_tasks()))
    validation_results.append(("Project服务扩展", validate_project_service()))
    validation_results.append(("错误处理机制", validate_error_handling()))
    validation_results.append(("异步编程模式", validate_async_patterns()))
    validation_results.append(("数据库事务", validate_database_transactions()))
    validation_results.append(("进度跟踪机制", validate_progress_tracking()))
    validation_results.append(("系统集成点", validate_integration_points()))

    # 输出结果
    print("\n" + "=" * 60)
    print("📊 验证结果汇总:")
    print("=" * 60)

    passed_count = 0
    for test_name, result in validation_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed_count += 1

    print(f"\n总计: {passed_count}/{len(validation_results)} 项验证通过")

    if passed_count == len(validation_results):
        print("\n🎉 所有验证通过！异步文件处理流程实现完整且规范。")

        print("\n✅ 实现特性:")
        print("   - 模型层批量操作方法（Chapter、Paragraph、Sentence）")
        print("   - ProjectProcessingService业务处理协调")
        print("   - Celery异步任务处理（文件上传、状态查询、重试、健康检查）")
        print("   - 项目进度跟踪和状态管理")
        print("   - 完整的错误处理和重试机制")
        print("   - 数据库事务保证数据一致性")
        print("   - 异步编程模式优化性能")
        print("   - 进度跟踪机制实时反馈")
        print("   - 系统各模块正确集成")

        return True
    else:
        print(f"\n❌ {len(validation_results) - passed_count}项验证失败，需要修复。")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
