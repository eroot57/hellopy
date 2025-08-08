import streamlit as st
import subprocess
import os
import time

# Set page configuration
st.set_page_config(
    page_title="File Download App",
    page_icon="⬇️",
    layout="wide"
)

# Display the main title
st.title("Hello")
st.subheader("Server File Download and Explorer")

# Function to run shell command safely
def run_shell_command(command, timeout=30):
    try:
        # Run the command and capture output
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

# Display current working directory
st.markdown("### Current Directory:")
current_dir = os.getcwd()
st.code(current_dir)

# Download section
st.markdown("### Download PacketCrypt")

if st.button("📥 Download PacketCrypt Binary", type="primary"):
    with st.spinner("Downloading file... This may take a moment..."):
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run wget command
        wget_cmd = "wget https://github.com/cjdelisle/packetcrypt_rs/releases/download/packetcrypt-v0.6.0/packetcrypt-v0.6.0-linux_amd64 -O ppp"
        status_text.text("Running wget command...")
        progress_bar.progress(25)
        
        result = run_shell_command(wget_cmd, timeout=60)  # 60 second timeout for download
        
        progress_bar.progress(75)
        
        if result['success']:
            st.success("✅ Download completed successfully!")
            if result['stdout']:
                st.text("Wget output:")
                st.code(result['stdout'])
        else:
            st.error(f"❌ Download failed: {result['stderr']}")
            if result['stdout']:
                st.text("Wget output:")
                st.code(result['stdout'])
        
        progress_bar.progress(100)
        status_text.text("Download process completed.")
        
        # Small delay before refreshing file list
        time.sleep(1)
        st.rerun()

# File listing section
st.markdown("---")
st.markdown("### Files and Folders:")

# Run ls command and display results
file_list_result = run_shell_command("ls -la")

if not file_list_result['success']:
    st.error(f"Error running ls command: {file_list_result['stderr']}")
else:
    file_list = file_list_result['stdout']
    
    # Display the raw output in a code block
    with st.expander("Raw ls output", expanded=False):
        st.code(file_list, language="bash")
    
    # Create a more user-friendly display
    st.markdown("### Formatted View:")
    
    # Parse the ls -la output (skip the first line which is total)
    lines = file_list.split('\n')
    if lines and lines[0].startswith('total'):
        lines = lines[1:]
    
    # Create columns for better display
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
                    # Add emoji based on file type and highlight downloaded file
                    if name == "ppp":
                        st.text(f"🎯 {name} (Downloaded)")
                    elif permissions.startswith('d'):
                        st.text(f"📁 {name}")
                    elif permissions[3] == 'x' or permissions[6] == 'x' or permissions[9] == 'x':
                        st.text(f"⚡ {name}")
                    else:
                        st.text(f"📄 {name}")

# Add manual refresh button
if st.button("🔄 Refresh File List"):
    st.rerun()

# Add some spacing and info
st.markdown("---")
st.info("💡 Click 'Download PacketCrypt Binary' to download the file as 'ppp', then the file list will automatically refresh.")
st.caption("This app downloads PacketCrypt binary and shows the updated file listing.")
