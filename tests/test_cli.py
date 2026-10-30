#!/usr/bin/env python3
"""Atlas Runtime Engine — CLI and Integration Tests."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, ".."))
CLI_PATH = os.path.join(ROOT_DIR, "runtime", "cli.py")


class TestCLIIntegration(unittest.TestCase):
    def run_cli(self, args, cwd=None):
        """Run CLI in subprocess via Python executable."""
        cmd = [sys.executable, CLI_PATH] + args
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd or ROOT_DIR
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_cli_help(self):
        code, out, err = self.run_cli(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage: atlas", out)
        self.assertIn("--brief", out)
        self.assertIn("--category", out)

    def test_cli_version(self):
        code, out, err = self.run_cli(["--version"])
        self.assertEqual(code, 0)
        # On Python argparse, action="version" prints to stdout or stderr depending on Python version
        version_output = out or err
        self.assertIn("Atlas Runtime v2.0.0", version_output)
        self.assertIn("Library v2.0.0", version_output)

    def test_cli_validate_only(self):
        code, out, err = self.run_cli(["--validate-only"])
        self.assertEqual(code, 0)
        self.assertIn("[OK] Library v2.0.0 validated successfully", err)

    def test_cli_generate_json_plan_from_flags(self):
        code, out, err = self.run_cli(["--category", "saas", "--tones", "minimal", "--format", "json"])
        self.assertEqual(code, 0)
        # Parse stdout as JSON
        data = json.loads(out)
        self.assertEqual(data["runtime_version"], "2.0.0")
        self.assertEqual(data["normalized_brief"]["category"], "saas")
        self.assertIn("art_direction", data)
        self.assertIn("composition", data)

    def test_cli_generate_from_brief_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            brief_file = os.path.join(tmpdir, "test_brief.json")
            with open(brief_file, "w", encoding="utf-8") as f:
                json.dump({"category": "fintech", "tones": ["bold", "luxury"]}, f)

            code, out, err = self.run_cli(["--brief", brief_file])
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(data["normalized_brief"]["category"], "fintech")

    def test_cli_output_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "plan.json")
            code, out, err = self.run_cli(["--category", "education", "--output", out_file])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.isfile(out_file))
            with open(out_file, "r", encoding="utf-8") as f:
                saved_plan = json.load(f)
            self.assertEqual(saved_plan["normalized_brief"]["category"], "education")

    def test_cli_invalid_brief_file_exits_code_1(self):
        code, out, err = self.run_cli(["--brief", "non_existent_file.json"])
        self.assertEqual(code, 1)
        self.assertIn("[ERROR]", err)

    def test_cli_invalid_page_type_exits_code_1(self):
        code, out, err = self.run_cli(["--page-type", "unsupported_type"])
        self.assertNotEqual(code, 0)

    def test_cli_working_directory_independence(self):
        # Execute from workspace root or system temp dir
        code, out, err = self.run_cli(["--category", "saas", "--format", "summary"], cwd=WORKSPACE_ROOT)
        self.assertEqual(code, 0)
        self.assertIn("ATLAS DESIGN PLAN", out)


if __name__ == "__main__":
    unittest.main()

