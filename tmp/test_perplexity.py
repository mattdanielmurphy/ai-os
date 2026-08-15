import subprocess

def test_length(char_count):
    secret = f"BANANA_{char_count}"
    prompt = f"What is the secret code at the very end of this message? Please reply with JUST the secret code.\\n\\n"
    prompt += "A" * char_count
    prompt += f"\\n\\nThe secret code is: {secret}"
    
    print(f"Testing {char_count} characters...")
    try:
        result = subprocess.run(
            ["node", "/Users/matt/projects/external/Proxima/cli/proxima-cli.cjs", "ask", "perplexity", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout.strip()
        if secret in output or secret.lower() in output.lower():
            print(f"✅ Success at {char_count} characters! Output: {output[:100]}")
            return True
        else:
            print(f"❌ Failed at {char_count} characters. Output did not contain secret. Output: {output[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⚠️ Timeout at {char_count} characters.")
        return False
    except Exception as e:
        print(f"⚠️ Error at {char_count} characters: {e}")
        return False

for length in [10000, 20000, 30000, 40000]:
    test_length(length)
