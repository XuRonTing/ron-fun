#!/usr/bin/env python
"""
Ron.fun 测试运行脚本

用于运行所有测试或特定类别的测试，并生成报告
使用方法:
    python tests/run_tests.py  # 运行所有测试
    python tests/run_tests.py --api  # 只运行API测试
    python tests/run_tests.py --unit  # 只运行单元测试
    python tests/run_tests.py --report  # 生成测试报告
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "tests" / "reports"


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="运行Ron.fun项目测试")
    parser.add_argument("--api", action="store_true", help="只运行API测试")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--service", action="store_true", help="只运行服务测试")
    parser.add_argument("--db", action="store_true", help="只运行数据库测试")
    parser.add_argument("--performance", action="store_true", help="只运行性能测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--report", action="store_true", help="生成HTML测试报告")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    parser.add_argument("--xvs", action="store_true", help="用于在Visual Studio Code中查看测试输出")
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    os.chdir(PROJECT_ROOT)
    
    # 创建报告目录（如果不存在）
    if args.report and not REPORTS_DIR.exists():
        REPORTS_DIR.mkdir(parents=True)
    
    # 构建pytest命令
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.xvs:
        cmd.append("--no-header")
        cmd.append("--no-summary")
        cmd.append("-q")
    
    # 添加标记参数
    if args.api:
        cmd.append("-m")
        cmd.append("api")
    elif args.unit:
        cmd.append("-m")
        cmd.append("unit")
    elif args.service:
        cmd.append("-m")
        cmd.append("service")
    elif args.db:
        cmd.append("-m")
        cmd.append("db")
    elif args.performance:
        cmd.append("-m")
        cmd.append("performance")
    elif args.integration:
        cmd.append("-m")
        cmd.append("integration")
    
    # 添加报告参数
    if args.report:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        report_file = REPORTS_DIR / f"test_report_{timestamp}.html"
        cov_report_file = REPORTS_DIR / f"coverage_report_{timestamp}"
        
        cmd.extend([
            "--html", str(report_file),
            "--self-contained-html",
            "--cov=app",
            f"--cov-report=html:{cov_report_file}",
            "--cov-report=term"
        ])
    
    # 打印将要执行的命令
    print(f"执行命令: {' '.join(cmd)}")
    
    # 运行测试
    result = subprocess.run(cmd)
    
    # 返回测试结果状态码
    return result.returncode


if __name__ == "__main__":
    sys.exit(main()) 