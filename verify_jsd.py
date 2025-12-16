from cloudscraper.jsd_solver import JSDSolver
from cloudscraper.lz_string_custom import CustomLZString
import json

def test_lz_string():
    print("Testing CustomLZString...")
    # Basic smoke test for custom LZString
    # Since we don't have a reference decompressor for the custom key, 
    # we'll checks for consistency and exception freedom.
    key = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"
    input_str = '{"test":"value"}'
    
    compressed = CustomLZString.compress_to_encoded_uri_component(input_str, key)
    print(f"Input: {input_str}")
    print(f"Compressed (len={len(compressed)}): {compressed}")
    assert len(compressed) > 0, "Compression should produce output"
    print("CustomLZString test passed.")

def test_jsd_solver_parsing():
    print("\nTesting JSDSolver Parsing...")
    # Mock script content based on regex expectations
    # lzKeyRegex = `[^\s,]*\$[^\s,]*\+?[^\s,]*`
    # sKeyRegex = `\d+\.\d+:\d+:[^\s,]+`
    
    # We need 2 matches for each.
    # lzKey comes second.
    mock_script = """
    var x = "dummy$key+1";
    var y = "REAL$KEY+ALPHABET"; 
    
    var a = "1.1:123:dummy";
    var b = "2.2:456:SECRET_KEY";
    """
    
    solver = JSDSolver()
    lz_key, s_key = solver.parse_script(mock_script)
    
    print(f"Parsed LZ Key: {lz_key}")
    print(f"Parsed Secret Key: {s_key}")
    
    assert lz_key == "REAL$KEY+ALPHABET"
    assert s_key == "2.2:456:SECRET_KEY"
    print("Parsing test passed.")

def test_jsd_solver_flow():
    print("\nTesting JSDSolver Flow...")
    mock_script = """
    var y = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$"; 
    var y_dummy = "dummy";
    var b = "0.0:0:SECRET";
    var b_dummy = "dummy";
    """
    
    solver = JSDSolver(user_agent="Mozilla/5.0 Test")
    # Note: Regex expects 2 matches.
    # Re-craft mock to ensure 2 matches
    mock_script = """
    var k1 = "junk$k+1";
    var k2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-$";
    var s1 = "1.1:1:junk";
    var s2 = "2.2:2:THE_SECRET";
    """
    
    result = solver.solve(mock_script)
    print("Solver Result keys:", result.keys())
    print("Secret:", result['s'])
    print("Window Props (compressed):", result['wp'])
    
    assert result['s'] == "2.2:2:THE_SECRET"
    assert len(result['wp']) > 10
    print("Flow test passed.")

if __name__ == "__main__":
    try:
        test_lz_string()
        test_jsd_solver_parsing()
        test_jsd_solver_flow()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
