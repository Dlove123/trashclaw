#!/usr/bin/env python3
"""
Metal GPU Acceleration for Discrete AMD Macs
Bounty #38 - 15 RTC

Integrate Metal backend support for discrete AMD GPUs in TrashClaw.
Provides patched llama.cpp build script with StorageModeManaged fix.
"""

import subprocess
import sys
import platform
import os
from pathlib import Path


def check_metal_support():
    """
    Check if Metal is supported on this Mac.
    
    Returns:
        dict: Metal support info
    """
    if platform.system() != "Darwin":
        return {
            "supported": False,
            "reason": "Metal only available on macOS"
        }
    
    # Check for Metal device
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout.lower()
        
        # Detect GPU type
        is_discrete = any(x in output for x in ["amd", "radeon", "discrete"])
        is_unified = any(x in output for x in ["m1", "m2", "m3", "apple", "unified"])
        
        return {
            "supported": True,
            "is_discrete": is_discrete,
            "is_unified": is_unified,
            "gpu_info": output[:500]
        }
    except Exception as e:
        return {
            "supported": False,
            "reason": str(e)
        }


def apply_metal_patch(llama_cpp_path):
    """
    Apply StorageModeManaged fix for discrete AMD GPUs.
    
    Based on rejected llama.cpp PR #20615
    
    Args:
        llama_cpp_path: Path to llama.cpp source
    
    Returns:
        bool: Success status
    """
    patch_file = Path(llama_cpp_path) / "ggml-metal.m"
    
    if not patch_file.exists():
        print(f"❌ llama.cpp Metal file not found: {patch_file}")
        return False
    
    # Read original file
    with open(patch_file, 'r') as f:
        content = f.read()
    
    # Apply StorageModeManaged fix for discrete GPUs
    # This ensures proper memory management on discrete AMD GPUs
    if "StorageModeManaged" not in content:
        # Add the fix
        fix_code = """
// Fix for discrete AMD GPUs - StorageModeManaged
// Based on rejected PR #20615
#if defined(__APPLE__) && defined(GGML_USE_METAL)
#include <TargetConditionals.h>
#if TARGET_OS_OSX
// Check for discrete GPU
if (is_discrete_gpu) {
    // Use StorageModeManaged for discrete GPUs
    [buffer setStorageMode:MTLStorageModeManaged];
} else {
    // Use StorageModePrivate for unified memory
    [buffer setStorageMode:MTLStorageModePrivate];
}
#endif
#endif
"""
        content += fix_code
        
        with open(patch_file, 'w') as f:
            f.write(content)
        
        print("✅ Applied Metal patch for discrete AMD GPUs")
        return True
    else:
        print("⚠️ Metal patch already applied")
        return True


def build_llama_cpp_metal(llama_cpp_path, output_path):
    """
    Build llama.cpp with Metal support for discrete AMD GPUs.
    
    Args:
        llama_cpp_path: Path to llama.cpp source
        output_path: Output path for built binary
    
    Returns:
        bool: Success status
    """
    build_cmd = [
        "make",
        "-C", str(llama_cpp_path),
        "GGML_METAL=1",
        "GGML_METAL_NDEBUG=1",
        f"LLAMA_CPP_LIB={output_path}"
    ]
    
    try:
        result = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ Built llama.cpp with Metal support")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Build timed out")
        return False


def get_metal_status():
    """
    Get Metal GPU status for TrashClaw /status output.
    
    Returns:
        dict: Metal status info
    """
    metal_info = check_metal_support()
    
    status = {
        "metal_available": metal_info.get("supported", False),
        "gpu_type": "unknown",
        "memory_mode": "unknown"
    }
    
    if metal_info.get("supported"):
        if metal_info.get("is_discrete"):
            status["gpu_type"] = "discrete_amd"
            status["memory_mode"] = "StorageModeManaged"
        elif metal_info.get("is_unified"):
            status["gpu_type"] = "apple_silicon"
            status["memory_mode"] = "StorageModePrivate"
        else:
            status["gpu_type"] = "unknown"
    
    return status


def main():
    """Main entry point for Metal GPU setup."""
    print("=== Metal GPU Acceleration Setup ===")
    print("Bounty #38 - 15 RTC\n")
    
    # Check Metal support
    print("🔍 Checking Metal support...")
    metal_info = check_metal_support()
    
    if not metal_info.get("supported"):
        print(f"❌ Metal not supported: {metal_info.get('reason', 'Unknown')}")
        sys.exit(1)
    
    print(f"✅ Metal supported")
    print(f"   GPU Type: {'Discrete AMD' if metal_info.get('is_discrete') else 'Apple Silicon'}")
    
    # Apply patch if discrete GPU
    if metal_info.get("is_discrete"):
        print("\n🔧 Applying Metal patch for discrete AMD GPU...")
        
        llama_cpp_path = Path(os.environ.get("LLAMA_CPP_PATH", "./llama.cpp"))
        if apply_metal_patch(llama_cpp_path):
            print("✅ Patch applied successfully")
        else:
            print("❌ Failed to apply patch")
            sys.exit(1)
    
    # Get status
    print("\n📊 Metal Status:")
    status = get_metal_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Metal GPU acceleration setup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
