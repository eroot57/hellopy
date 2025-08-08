import streamlit as st
import subprocess
import os
import time
import threading

# Set page configuration
st.set_page_config(
    page_title="PacketCrypt Mining App",
    page_icon="⛏️",
    layout="wide"
)

# Display the main title
st.title("Hello")
st.subheader("PacketCrypt Mining Setup and Runner")

# Function to run shell command safely
def run_shell_command(command, timeout=30, stream_output=False):
    try:
        if stream_output:
            # For streaming output (like mining) - capture both stdout and stderr
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            return process
        else:
            # For regular commands
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            return {
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
            
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': -1,
            'success': False
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'returncode': -1,
            'success': False
        }

# Initialize session state for mining process
if 'mining_process' not in st.session_state:
    st.session_state.mining_process = None
if 'mining_output' not in st.session_state:
    st.session_state.mining_output = []
if 'raw_log' not in st.session_state:
    st.session_state.raw_log = ""

# Display current working directory
st.markdown("### Current Directory:")
current_dir = os.getcwd()
st.code(current_dir)

# Step 1: Download section
st.markdown("### Step 1: Download PacketCrypt Binary")

if st.button("📥 Download with curl", type="primary"):
    with st.spinner("Downloading with curl... This may take a moment..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run curl command
        curl_cmd = "curl -L https://github.com/cjdelisle/packetcrypt_rs/releases/download/packetcrypt-v0.6.0/packetcrypt-v0.6.0-linux_amd64 -o ppp"
        status_text.text("Running curl command...")
        progress_bar.progress(25)
        
        result = run_shell_command(curl_cmd, timeout=120)  # 2 minute timeout for download
        
        progress_bar.progress(75)
        
        if result['success']:
            st.success("✅ Download completed successfully!")
        else:
            st.error(f"❌ Download failed: {result['stderr']}")
        
        if result['stdout']:
            st.text("Curl output:")
            st.code(result['stdout'])
            
        progress_bar.progress(100)
        status_text.text("Download process completed.")
        time.sleep(1)
        st.rerun()

# Step 2: File listing section
st.markdown("---")
st.markdown("### Step 2: Current Files")

# Run ls command and display results
file_list_result = run_shell_command("ls -la")

if not file_list_result['success']:
    st.error(f"Error running ls command: {file_list_result['stderr']}")
else:
    file_list = file_list_result['stdout']
    
    # Display formatted file list
    lines = file_list.split('\n')
    if lines and lines[0].startswith('total'):
        lines = lines[1:]
    
    # Check if ppp file exists
    ppp_exists = any('ppp' in line for line in lines if line.strip())
    
    if ppp_exists:
        st.success("✅ PacketCrypt binary (ppp) found!")
    else:
        st.warning("⚠️ PacketCrypt binary (ppp) not found. Please download first.")
    
    # Create columns for file display
    col1, col2, col3, col4 = st.columns([3, 2, 2, 4])
    
    with col1:
        st.write("**Permissions**")
    with col2:
        st.write("**Size**")
    with col3:
        st.write("**Date**")
    with col4:
        st.write("**Name**")
    
    st.markdown("---")
    
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 9:
                permissions = parts[0]
                size = parts[4]
                date = f"{parts[5]} {parts[6]} {parts[7]}"
                name = ' '.join(parts[8:])
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 4])
                
                with col1:
                    st.text(permissions)
                with col2:
                    st.text(size)
                with col3:
                    st.text(date)
                with col4:
                    if name == "ppp":
                        executable = permissions[3] == 'x' or permissions[6] == 'x' or permissions[9] == 'x'
                        if executable:
                            st.text(f"⛏️ {name} (Executable)")
                        else:
                            st.text(f"🎯 {name} (Downloaded)")
                    elif permissions.startswith('d'):
                        st.text(f"📁 {name}")
                    elif permissions[3] == 'x' or permissions[6] == 'x' or permissions[9] == 'x':
                        st.text(f"⚡ {name}")
                    else:
                        st.text(f"📄 {name}")

# Step 3: Mining section
st.markdown("---")
st.markdown("### Step 3: Start PacketCrypt Mining")

col1, col2 = st.columns(2)

with col1:
    if st.button("⛏️ Start Mining", type="primary", disabled=(st.session_state.mining_process is not None)):
        # First make executable
        chmod_cmd = "chmod +x ppp"
        chmod_result = run_shell_command(chmod_cmd)
        
        # Show chmod result
        st.text("CHMOD OUTPUT:")
        if chmod_result['stdout']:
            st.code(chmod_result['stdout'])
        if chmod_result['stderr']:
            st.code(f"STDERR: {chmod_result['stderr']}")
        
        # Now run the mining command and capture everything
        mining_cmd = "./ppp ann -p pkt1qfhr09kswj2hy0xgnzzj5r8ux09m7ltnuumf4xx http://pool.pkt.world"
        st.text(f"EXECUTING: {mining_cmd}")
        
        # Clear previous logs
        st.session_state.mining_output = []
        st.session_state.raw_log = ""
        
        # Start mining process
        st.session_state.mining_process = run_shell_command(mining_cmd, stream_output=True)
        
        # Immediately try to get some initial output
        time.sleep(3)
        
        # Get any immediate output
        initial_output = ""
        if st.session_state.mining_process:
            try:
                # Try to read initial lines
                for _ in range(10):  # Try to read up to 10 lines
                    try:
                        stdout_line = st.session_state.mining_process.stdout.readline()
                        if stdout_line:
                            initial_output += stdout_line
                        
                        stderr_line = st.session_state.mining_process.stderr.readline() 
                        if stderr_line:
                            initial_output += stderr_line
                            
                        if not stdout_line and not stderr_line:
                            break
                    except:
                        break
                
                # Show what we got immediately
                if initial_output:
                    st.text("INITIAL SHELL OUTPUT:")
                    st.code(initial_output)
                    st.session_state.raw_log = initial_output
                else:
                    st.text("NO IMMEDIATE OUTPUT - checking process status...")
                    
                # Check if process is still alive
                if st.session_state.mining_process.poll() is None:
                    st.text("PROCESS STATUS: Still running")
                else:
                    exit_code = st.session_state.mining_process.returncode
                    st.text(f"PROCESS STATUS: Exited with code {exit_code}")
                    
            except Exception as e:
                st.text(f"ERROR READING OUTPUT: {e}")

with col2:
    if st.button("🛑 Stop Mining", type="secondary", disabled=(st.session_state.mining_process is None)):
        if st.session_state.mining_process:
            st.session_state.mining_process.terminate()
            st.session_state.mining_process = None
            st.session_state.mining_output = []
            st.session_state.raw_log = ""
            st.success("🛑 Mining stopped")
            st.rerun()

# Display mining output
if st.session_state.mining_process:
    st.markdown("### Mining Status:")
    
    # Check if process is still running
    if st.session_state.mining_process.poll() is None:
        st.text("🔄 Process running - capturing live output...")
        
        # Try to read output from both stdout and stderr
        try:
            # Read from stdout
            stdout_line = st.session_state.mining_process.stdout.readline()
            if stdout_line:
                st.session_state.raw_log += stdout_line
                
            # Read from stderr  
            stderr_line = st.session_state.mining_process.stderr.readline()
            if stderr_line:
                st.session_state.raw_log += stderr_line
        except:
            pass
            
    else:
        # Process has ended - get all remaining output
        return_code = st.session_state.mining_process.returncode
        st.text(f"⚠️ Process ended with exit code: {return_code}")
        
        # Get any remaining output
        try:
            remaining_stdout, remaining_stderr = st.session_state.mining_process.communicate(timeout=2)
            if remaining_stdout:
                st.session_state.raw_log += remaining_stdout
            if remaining_stderr:
                st.session_state.raw_log += remaining_stderr
        except:
            pass
        
        st.session_state.mining_process = None
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📝 Raw Shell Output", "💾 Download Log"])
    
    with tab1:
        st.markdown("**Exact Shell Console Output:**")
        if st.session_state.raw_log:
            # Show the exact console output in a text area
            st.text_area(
                "Shell Console Log", 
                value=st.session_state.raw_log,
                height=400,
                disabled=True,
                key="shell_log_display"
            )
        else:
            st.text("No console output yet...")
    
    with tab2:
        if st.session_state.raw_log:
            # Add download button for the log
            if st.download_button(
                label="💾 Download Shell Log",
                data=st.session_state.raw_log,
                file_name=f"shell_log_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            ):
                st.success("📥 Shell log downloaded!")
        else:
            st.text("No log data to download yet...")

# Auto-refresh while mining (but not immediately after starting)
if st.session_state.mining_process and st.session_state.mining_process.poll() is None:
    time.sleep(2)
    st.rerun()

# Manual refresh button
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Refresh"):
        st.rerun()

with col2:
    if st.button("🧹 Clear Logs"):
        st.session_state.mining_output = []
        st.session_state.raw_log = ""
        st.success("Logs cleared!")
        st.rerun()

# Add info section
st.markdown("---")
st.info("💡 Steps: 1) Download binary with curl, 2) Check files, 3) Start mining (automatically makes executable)")
st.caption("Mining address: pkt1qfhr09kswj2hy0xgnzzj5r8ux09m7ltnuumf4xx | Pool: http://pool.pkt.world")
