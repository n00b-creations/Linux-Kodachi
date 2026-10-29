import os
from pathlib import Path
import shutil
import subprocess


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "uninstall-overlay.sh"


def run_dry_run(tmp_path, *args):
    paths = {
        "CYBER_OS_PREFIX": tmp_path / "prefix",
        "CYBER_OS_CONFIG": tmp_path / "config",
        "CYBER_OS_STATE": tmp_path / "state",
        "CYBER_OS_LOG": tmp_path / "log",
        "CYBER_OS_DESKTOP": tmp_path / "desktop" / "cyber-os.desktop",
    }
    env = os.environ.copy()
    env.update({name: str(path) for name, path in paths.items()})
    result = subprocess.run([shutil.which("bash"), str(SCRIPT), "--dry-run", *args], env=env, capture_output=True, text=True, check=False)
    return result, paths


def test_uninstaller_dry_run_preserves_data_by_default(tmp_path):
    result, paths = run_dry_run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert f"Would remove: {paths['CYBER_OS_PREFIX']}" in result.stdout.splitlines()
    assert f"Preserved configuration: {paths['CYBER_OS_CONFIG']}" in result.stdout
    assert f"Preserved state:         {paths['CYBER_OS_STATE']}" in result.stdout
    assert f"Preserved logs:          {paths['CYBER_OS_LOG']}" in result.stdout
    assert f"Would remove: {paths['CYBER_OS_CONFIG']}" not in result.stdout
    assert f"Would remove: {paths['CYBER_OS_STATE']}" not in result.stdout
    assert f"Would remove: {paths['CYBER_OS_LOG']}" not in result.stdout


def test_uninstaller_purge_plan_includes_data_only_when_requested(tmp_path):
    result, paths = run_dry_run(tmp_path, "--purge-data")
    assert result.returncode == 0, result.stderr
    for name in ("CYBER_OS_CONFIG", "CYBER_OS_STATE", "CYBER_OS_LOG"):
        assert f"Would remove: {paths[name]}" in result.stdout.splitlines()


def test_uninstaller_rejects_overlapping_paths(tmp_path):
    env = os.environ.copy()
    env.update({
        "CYBER_OS_PREFIX": str(tmp_path / "install"),
        "CYBER_OS_CONFIG": str(tmp_path / "install" / "config"),
        "CYBER_OS_STATE": str(tmp_path / "state"),
        "CYBER_OS_LOG": str(tmp_path / "log"),
        "CYBER_OS_DESKTOP": str(tmp_path / "desktop" / "cyber-os.desktop"),
    })
    result = subprocess.run([shutil.which("bash"), str(SCRIPT), "--dry-run"], env=env, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "overlapping uninstall paths" in result.stderr


def test_uninstaller_rejects_unknown_option(tmp_path):
    result, _ = run_dry_run(tmp_path, "--not-an-option")
    assert result.returncode == 2
    assert "Unknown option" in result.stderr


def test_uninstaller_dry_run_does_not_follow_symlink_targets(tmp_path):
    actual_prefix = tmp_path / "real-prefix"
    actual_prefix.mkdir()
    prefix_link = tmp_path / "prefix-link"
    prefix_link.symlink_to(actual_prefix, target_is_directory=True)
    env = os.environ.copy()
    env.update({
        "CYBER_OS_PREFIX": str(prefix_link),
        "CYBER_OS_CONFIG": str(tmp_path / "config"),
        "CYBER_OS_STATE": str(tmp_path / "state"),
        "CYBER_OS_LOG": str(tmp_path / "log"),
        "CYBER_OS_DESKTOP": str(tmp_path / "desktop" / "cyber-os.desktop"),
    })
    result = subprocess.run([shutil.which("bash"), str(SCRIPT), "--dry-run"], env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert f"Would remove: {prefix_link}" in result.stdout
    assert f"Would remove: {actual_prefix}" not in result.stdout


def test_uninstaller_purge_requires_exact_confirmation(tmp_path):
    import pytest
    if os.geteuid() != 0:
        pytest.skip("The destructive-path confirmation check requires root in the test environment")
    env = os.environ.copy()
    paths = [tmp_path / "prefix", tmp_path / "config", tmp_path / "state", tmp_path / "log"]
    for path in paths:
        path.mkdir()
    env.update({
        "CYBER_OS_PREFIX": str(paths[0]),
        "CYBER_OS_CONFIG": str(paths[1]),
        "CYBER_OS_STATE": str(paths[2]),
        "CYBER_OS_LOG": str(paths[3]),
        "CYBER_OS_DESKTOP": str(tmp_path / "desktop" / "cyber-os.desktop"),
    })
    result = subprocess.run([shutil.which("bash"), str(SCRIPT), "--purge-data"], env=env, input="NO\n", capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "Data purge cancelled" in result.stdout
    assert all(path.is_dir() for path in paths)
