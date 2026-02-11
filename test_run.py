"""
Test script to verify all blog-writing-agent components work.
Run from project root: python test_run.py
"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

passed = 0
failed = 0

# --- Schemas ---
print("\n--- Schemas ---")
from Schemas.evidence_schema import EvidenceItem, EvidencePack
from Schemas.image_schema import ImageSpec, GlobalImagePlan
from Schemas.plan_schema import Plan
from Schemas.router_schema import RouterDecision
from Schemas.task_schema import Task

def run_schema_tests():
    global passed, failed
    # evidence
    try:
        item = EvidenceItem(title="Test", url="https://example.com")
        pack = EvidencePack(evidence=[item])
        print("  [PASS] evidence_schema")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] evidence_schema: {e}")
        failed += 1
    # image
    try:
        spec = ImageSpec(placeholders="[[IMAGE_1]]", filename="test.png", alt="alt", caption="cap", prompt="p")
        plan = GlobalImagePlan(md_with_placeholders="# Title", images=[spec])
        print("  [PASS] image_schema")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] image_schema: {e}")
        failed += 1
    # plan + task
    try:
        task = Task(id=1, title="Intro", goal="Learn", bullets=["a","b","c"], target_words=150)
        plan = Plan(blog_title="Test", audience="devs", tone="formal", tasks=[task])
        print("  [PASS] plan_schema, task_schema")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] plan_schema/task_schema: {e}")
        failed += 1
    # router
    try:
        d = RouterDecision(needs_research=False, mode="closed_book", reason="Test")
        print("  [PASS] router_schema")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] router_schema: {e}")
        failed += 1

# --- State ---
print("\n--- State ---")
def run_state_test():
    global passed, failed
    try:
        from state.State import Blog_State
        # TypedDict - just check import
        print("  [PASS] State.Blog_State")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] State: {e}")
        failed += 1

# --- Nodes (imports only - no API calls) ---
print("\n--- Nodes (import check) ---")
def run_node_import_tests():
    global passed, failed
    # orches_node
    try:
        from nodes.orches_node import orchestrator_node, fanout
        print("  [PASS] orches_node (orchestrator_node, fanout)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] orches_node: {e}")
        failed += 1
    # tavily_research
    try:
        from nodes.tavily_research import research_node, _tavily_search
        print("  [PASS] tavily_research")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] tavily_research: {e}")
        failed += 1
    # merging_node
    try:
        from nodes.merging_node import merge_content, decide_images
        print("  [PASS] merging_node")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] merging_node: {e}")
        failed += 1
    # Worker_node
    try:
        from nodes.Worker_node import worker_node
        print("  [PASS] Worker_node")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Worker_node: {e}")
        failed += 1
    # Router (file has space in name)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "router_node",
            os.path.join(os.path.dirname(__file__), "nodes", "Router_Node.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "Router_Node")
        assert hasattr(mod, "route_next")
        print("  [PASS] Router_Node")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Router_Node: {e}")
        failed += 1

# --- Node logic (no API) ---
print("\n--- Nodes (logic - merge_content only, no API) ---")
def run_merge_logic_test():
    global passed, failed
    try:
        from nodes.merging_node import merge_content
        state = {
            "plan": type("Plan", (), {"blog_title": "My Blog"})(),
            "sections": [(1, "## Intro\nContent"), (2, "## Body\nMore")],
        }
        out = merge_content(state)
        assert "merged_md" in out
        assert "My Blog" in out["merged_md"]
        assert "## Intro" in out["merged_md"]
        print("  [PASS] merge_content logic")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] merge_content: {e}")
        failed += 1

# --- Full pipeline (optional - needs OpenAI + optional Tavily API keys) ---
# Set RUN_LIVE=1 to test Router + Orchestrator with real API
print("\n--- Full run (Router + Orchestrator - needs OPENAI_API_KEY) ---")
def run_full_test():
    global passed, failed
    if os.getenv("RUN_LIVE") != "1":
        print("  [SKIP] Set RUN_LIVE=1 to test Router + Orchestrator (skipping to avoid timeout)")
        return
    if not os.getenv("OPENAI_API_KEY"):
        print("  [SKIP] OPENAI_API_KEY not set - skipping LLM tests")
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "router_node",
            os.path.join(os.path.dirname(__file__), "nodes", "Router_Node.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        Router_Node = mod.Router_Node

        state = {"topic": "Python decorators basics", "evidence": [], "sections": []}
        out = Router_Node(state)
        assert "needs_research" in out
        assert "mode" in out
        assert "queries" in out
        print("  [PASS] Router_Node (live LLM)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Router_Node live: {e}")
        failed += 1

    try:
        from nodes.orches_node import orchestrator_node
        state = {
            "topic": "Python decorators basics",
            "mode": "closed_book",
            "evidence": [],
        }
        out = orchestrator_node(state)
        assert "plan" in out
        assert out["plan"].blog_title
        assert len(out["plan"].tasks) >= 1
        print("  [PASS] orchestrator_node (live LLM)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] orchestrator_node live: {e}")
        failed += 1

# --- Main ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("=" * 50)
    print("Blog Writing Agent - Test Run")
    print("=" * 50)

    run_schema_tests()
    run_state_test()
    run_node_import_tests()
    run_merge_logic_test()
    run_full_test()

    print("\n" + "=" * 50)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 50)
    sys.exit(1 if failed > 0 else 0)
