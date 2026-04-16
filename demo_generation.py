"""
demo_generation.py
------------------
Standalone demonstration of the Strategy Pattern for song generation.
Run with:
    python demo_generation.py mock
    python demo_generation.py suno
"""

import sys
import json
import os

# ---------------------------------------------------------------------------
# Minimal Django-free bootstrap so we can import our strategy classes
# directly from the command line without starting the full server.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

# Patch django.conf.settings so imports that do `from django.conf import settings`
# work without a full Django setup.
class _MockSettings:
    SUNO_API_KEY = os.environ.get("SUNO_API_KEY", "")
    GENERATOR_STRATEGY = os.environ.get("GENERATOR_STRATEGY", "mock")

import django.conf
django.conf.settings.configure(
    INSTALLED_APPS=[],
    DATABASES={},
    SUNO_API_KEY=os.environ.get("SUNO_API_KEY", ""),
    GENERATOR_STRATEGY=os.environ.get("GENERATOR_STRATEGY", "mock"),
)

from domain.generation.mock_strategy import MockSongGeneratorStrategy
from domain.generation.suno_strategy import SunoSongGeneratorStrategy

# ---------------------------------------------------------------------------
SAMPLE_REQUEST = {
    "prompt": "A calm piano melody about rain and nostalgia",
    "style":  "Classical",
    "title":  "Rainy Memories",
}

def pp(obj):
    print(json.dumps(obj, indent=2, default=str))

# ---------------------------------------------------------------------------
def run_mock():
    print("=" * 60)
    print("  STRATEGY A — Mock (Offline / Deterministic)")
    print("=" * 60)
    print("\n[1] Calling MockSongGeneratorStrategy.generate() ...\n")
    strategy = MockSongGeneratorStrategy()
    result = strategy.generate(SAMPLE_REQUEST)
    pp(result)
    task_id = result["task_id"]

    print(f"\n[2] Calling check_status(task_id='{task_id}') ...\n")
    status = strategy.check_status(task_id)
    pp(status)
    print("\n[OK] Mock strategy works - returned SUCCESS immediately with placeholder URLs.\n")

# ---------------------------------------------------------------------------
def run_suno():
    api_key = os.environ.get("SUNO_API_KEY", "")
    if not api_key:
        print("ERROR: SUNO_API_KEY env var is not set.")
        sys.exit(1)

    print("=" * 60)
    print("  STRATEGY B — Suno API (Real AI Generation)")
    print("=" * 60)
    print(f"\n  API key: {api_key[:8]}****{api_key[-4:]}")
    print("\n[1] Calling SunoSongGeneratorStrategy.generate() ...\n")
    strategy = SunoSongGeneratorStrategy()
    result = strategy.generate(SAMPLE_REQUEST)
    pp(result)
    task_id = result.get("task_id", "")

    if not task_id:
        print("\n[FAIL] No taskId returned from Suno API. Check your API key.\n")
        sys.exit(1)

    print(f"\n[2] Calling check_status(task_id='{task_id}') ...\n")
    status_result = strategy.check_status(task_id)
    pp(status_result)
    print(f"\n[OK] Suno strategy works - taskId '{task_id}' created, status: {status_result.get('status')}.")
    print("     Keep polling GET /api/generate/<task_id>/status/ until status == SUCCESS.\n")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "mock"
    if mode == "suno":
        run_suno()
    else:
        run_mock()
