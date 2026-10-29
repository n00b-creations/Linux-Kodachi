from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
KDASH = ROOT / "frontend" / "kdash"


def test_dashboard_loads_mapping_utility_before_single_app_runtime():
    html = (KDASH / "index.html").read_text()
    app = (KDASH / "app.js").read_text()
    assert html.index('src="app.mapping.js"') < html.index('src="app.js"')
    assert app.count("new THREE.WebGLRenderer") == 1
    assert "openMappingBtn.addEventListener" in app
    assert "mappedCategory(name) || guessCategoryFromName(name)" in app
    assert "config/node_map.yaml" in app


def test_mapping_utility_parses_and_matches_default_yaml():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is not installed")
    script = r"""
const api = require('./app.mapping.js');
const mapping = globalThis.KdashMapping;
const fs = require('fs');
const yaml = fs.readFileSync('config/node_map.yaml', 'utf8');
const parsed = mapping.parseNodeMap(yaml);
if (parsed.home !== 'home' || parsed.network !== 'network') process.exit(1);
if (mapping.categoryForNode('primary network router', parsed) !== 'network') process.exit(2);
if (mapping.categoryForNode('unmapped node', parsed) !== null) process.exit(3);
const serialized = mapping.stringifyNodeMap(parsed);
if (mapping.parseNodeMap(serialized).vcs !== 'vcs') process.exit(4);
let rejected = false;
try { mapping.parseNodeMap('device: unsafe'); } catch (error) { rejected = true; }
if (!rejected) process.exit(5);
"""
    result = subprocess.run([node, "-e", script], cwd=KDASH, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_dashboard_javascript_passes_node_syntax_check():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is not installed")
    for path in (KDASH / "app.js", KDASH / "app.mapping.js"):
        result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr
