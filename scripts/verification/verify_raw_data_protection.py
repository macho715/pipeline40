#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raw Data Protection Verification Script
=====================================

HVDC 파이프라인 실행 전후로 raw data 파일들의 무결성을 검증합니다.
MD5 해시, 수정 시간, 파일 크기를 비교하여 수정 여부를 확인합니다.

작성자: AI Development Team
버전: v1.0
작성일: 2025-10-23
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class RawDataVerifier:
    """Raw data 무결성 검증 클래스"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.raw_data_dir = project_root / "data" / "raw"
        self.logs_dir = project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # 검증 대상 raw data 파일들
        self.raw_files = [
            "Case List.xlsx",
            "HVDC Hitachi.xlsx"
        ]
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """파일의 MD5 해시를 계산합니다."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """파일 정보를 수집합니다."""
        try:
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "exists": True,
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "md5_hash": self.calculate_file_hash(file_path),
                "error": None
            }
        except Exception as e:
            return {
                "path": str(file_path),
                "exists": False,
                "size_bytes": 0,
                "modified_time": None,
                "md5_hash": None,
                "error": str(e)
            }
    
    def collect_baseline(self) -> Dict[str, Any]:
        """Raw data baseline을 수집합니다."""
        print("🔍 Raw data baseline 수집 중...")
        
        baseline = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "raw_data_dir": str(self.raw_data_dir),
            "files": {}
        }
        
        for filename in self.raw_files:
            file_path = self.raw_data_dir / filename
            print(f"  📄 {filename} 분석 중...")
            
            file_info = self.get_file_info(file_path)
            baseline["files"][filename] = file_info
            
            if file_info["exists"]:
                print(f"    ✅ 크기: {file_info['size_bytes']:,} bytes")
                print(f"    ✅ 수정시간: {file_info['modified_time']}")
                print(f"    ✅ MD5: {file_info['md5_hash'][:16]}...")
            else:
                print(f"    ❌ 파일 없음: {file_info['error']}")
        
        # Baseline 저장
        baseline_file = self.logs_dir / "raw_data_baseline.json"
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Baseline 저장: {baseline_file}")
        return baseline
    
    def verify_after_pipeline(self, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """파이프라인 실행 후 검증을 수행합니다."""
        print("\n🔍 Raw data 무결성 검증 중...")
        
        verification = {
            "timestamp": datetime.now().isoformat(),
            "baseline_timestamp": baseline["timestamp"],
            "verification_status": "PASS",
            "files": {},
            "summary": {
                "total_files": len(self.raw_files),
                "verified_files": 0,
                "modified_files": 0,
                "missing_files": 0,
                "error_files": 0
            }
        }
        
        for filename in self.raw_files:
            print(f"  📄 {filename} 검증 중...")
            
            file_path = self.raw_data_dir / filename
            current_info = self.get_file_info(file_path)
            baseline_info = baseline["files"].get(filename, {})
            
            file_verification = {
                "filename": filename,
                "baseline": baseline_info,
                "current": current_info,
                "status": "UNKNOWN",
                "changes": []
            }
            
            # 파일 존재 여부 확인
            if not current_info["exists"]:
                file_verification["status"] = "MISSING"
                file_verification["changes"].append("파일이 삭제되었습니다")
                verification["summary"]["missing_files"] += 1
                print(f"    ❌ 파일 없음")
            elif baseline_info.get("error"):
                file_verification["status"] = "ERROR"
                file_verification["changes"].append(f"Baseline 오류: {baseline_info['error']}")
                verification["summary"]["error_files"] += 1
                print(f"    ❌ Baseline 오류")
            else:
                # MD5 해시 비교
                if current_info["md5_hash"] != baseline_info["md5_hash"]:
                    file_verification["status"] = "MODIFIED"
                    file_verification["changes"].append("MD5 해시가 변경되었습니다")
                    verification["summary"]["modified_files"] += 1
                    print(f"    ❌ MD5 해시 변경")
                # 수정 시간 비교
                elif current_info["modified_time"] != baseline_info["modified_time"]:
                    file_verification["status"] = "MODIFIED"
                    file_verification["changes"].append("수정 시간이 변경되었습니다")
                    verification["summary"]["modified_files"] += 1
                    print(f"    ❌ 수정 시간 변경")
                # 파일 크기 비교
                elif current_info["size_bytes"] != baseline_info["size_bytes"]:
                    file_verification["status"] = "MODIFIED"
                    file_verification["changes"].append("파일 크기가 변경되었습니다")
                    verification["summary"]["modified_files"] += 1
                    print(f"    ❌ 파일 크기 변경")
                else:
                    file_verification["status"] = "UNCHANGED"
                    verification["summary"]["verified_files"] += 1
                    print(f"    ✅ 변경 없음")
            
            verification["files"][filename] = file_verification
        
        # 전체 검증 상태 결정
        if verification["summary"]["modified_files"] > 0 or verification["summary"]["missing_files"] > 0:
            verification["verification_status"] = "FAIL"
        
        return verification
    
    def generate_report(self, verification: Dict[str, Any]) -> str:
        """검증 결과 보고서를 생성합니다."""
        report_lines = [
            "# Raw Data Protection Verification Report",
            f"**생성 시간**: {verification['timestamp']}",
            f"**Baseline 시간**: {verification['baseline_timestamp']}",
            "",
            "## 📊 검증 요약",
            "",
            f"- **전체 파일**: {verification['summary']['total_files']}개",
            f"- **검증 완료**: {verification['summary']['verified_files']}개",
            f"- **수정 감지**: {verification['summary']['modified_files']}개",
            f"- **파일 없음**: {verification['summary']['missing_files']}개",
            f"- **오류 발생**: {verification['summary']['error_files']}개",
            "",
            f"## 🎯 전체 상태: **{verification['verification_status']}**",
            "",
            "## 📄 파일별 상세 결과",
            ""
        ]
        
        for filename, file_info in verification["files"].items():
            status_emoji = {
                "UNCHANGED": "✅",
                "MODIFIED": "❌",
                "MISSING": "⚠️",
                "ERROR": "💥"
            }.get(file_info["status"], "❓")
            
            report_lines.extend([
                f"### {status_emoji} {filename}",
                "",
                f"- **상태**: {file_info['status']}",
                f"- **파일 경로**: {file_info['current']['path']}",
                ""
            ])
            
            if file_info["changes"]:
                report_lines.append("**변경 사항**:")
                for change in file_info["changes"]:
                    report_lines.append(f"- {change}")
                report_lines.append("")
            
            # Baseline vs Current 비교
            if file_info["status"] != "UNCHANGED":
                report_lines.extend([
                    "**상세 비교**:",
                    "",
                    "| 항목 | Baseline | Current |",
                    "|------|----------|---------|"
                ])
                
                baseline = file_info["baseline"]
                current = file_info["current"]
                
                report_lines.extend([
                    f"| 파일 존재 | {'✅' if baseline.get('exists') else '❌'} | {'✅' if current.get('exists') else '❌'} |",
                    f"| 파일 크기 | {baseline.get('size_bytes', 0):,} bytes | {current.get('size_bytes', 0):,} bytes |",
                    f"| 수정 시간 | {baseline.get('modified_time', 'N/A')} | {current.get('modified_time', 'N/A')} |",
                    f"| MD5 해시 | {baseline.get('md5_hash', 'N/A')[:16] if baseline.get('md5_hash') else 'N/A'}... | {current.get('md5_hash', 'N/A')[:16] if current.get('md5_hash') else 'N/A'}... |",
                    ""
                ])
        
        report_content = "\n".join(report_lines)
        
        # 보고서 파일 저장
        report_file = self.logs_dir / "raw_data_verification_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"📋 검증 보고서 저장: {report_file}")
        return report_content

def main():
    """메인 실행 함수"""
    project_root = Path(__file__).resolve().parents[2]
    verifier = RawDataVerifier(project_root)
    
    print("=" * 80)
    print("HVDC Pipeline Raw Data Protection Verification")
    print("=" * 80)
    
    # 1. Baseline 수집
    baseline = verifier.collect_baseline()
    
    # 2. 파이프라인 실행 안내
    print("\n" + "=" * 80)
    print("📋 다음 단계:")
    print("1. 전체 파이프라인을 실행하세요: python run_pipeline.py --all")
    print("2. 실행 완료 후 이 스크립트를 다시 실행하여 검증하세요")
    print("=" * 80)
    
    return baseline

if __name__ == "__main__":
    main()
