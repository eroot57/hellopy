import streamlit as st
import subprocess
import os
import time

# Set page configuration
st.set_page_config(
    page_title="Download and File Explorer",
    page_icon="⬇️",
    layout="wide"
)

# Display the main title
st.title("Hello")
st.subheader("Download PacketCrypt and File Explorer")

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
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

# Display current working directory
st.markdown("### Current Directory:")
current_dir = os.getcwd()
st.code(current_dir)

# Download section
st.markdown("### Download PacketCrypt")
download_url = "https://github.com/cjdelisle/packetcrypt_rs/releases/download/packetcrypt-v0.6.0/packetcrypt-v0.6.0-linux_amd64"
output_filename = "ppp"

if st.button("⬇️ Download PacketCrypt", type="primary"):
    with st.spinner("Downloading PacketCrypt... This may take a moment."):
        # Show the command being executed
        wget_command = f'wget "{download_url}" -O {output_filename}'
        st.code(f"Executing: {wget_command}")
        
        # Run the wget command
        success, output = run_shell_command(wget_command, timeout=60)
        
        if success:
            st.success("✅ Download completed successfully!")
            if output:
                st.text("Download output:")
                st.code(output)
        else:
            st.error("❌ Download failed!")
            st.code(f"Error: {output}")
        
        # Auto-refresh the file list after download
        st.rerun()

# Check if file exists
file_exists = os.path.exists(output_filename)
if file_exists:
    file_size = os.path.getsize(output_filename)
    st.info(f"📁 File '{output_filename}' exists (Size: {file_size:,} bytes)")
    
    # Make executable button
    if st.button("🔧 Make Executable"):
        success, output = run_shell_command(f"chmod +x {output_filename}")
        if success:
            st.success("✅ File made executable!")
        else:
            st.error(f"❌ Failed to make executable: {output}")
        st.rerun()

# File listing section
st.markdown("---")
st.markdown("### Files and Folders (ls -la):")

# Get the file listing
success, file_list = run_shell_command("ls -la")

if not success:
    st.error(f"Error running ls command: {file_list}")
else:
    # Display the raw output in a code block
    st.code(file_list, language="bash")
    
    # Also create a more user-friendly display
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
                    # Add emoji based on file type and highlight our downloaded file
                    if name == output_filename:
                        if permissions.startswith('d'):
                            st.text(f"📁 🎯 {name}")
                        elif permissions[3] == 'x':
                            st.text(f"⚡ 🎯 {name}")
                        else:
                            st.text(f"📄 🎯 {name}")
                    else:
                        if permissions.startswith('d'):
                            st.text(f"📁 {name}")
                        elif permissions[3] == 'x':
                            st.text(f"⚡ {name}")
                        else:
                            st.text(f"📄 {name}")

# Add refresh button
if st.button("🔄 Refresh File List"):
    st.rerun()

# Add some spacing and info
st.markdown("---")
st.caption("This app downloads PacketCrypt binary and shows the file listing.")
st.caption("🎯 = Downloaded file | 📁 = Directory | ⚡ = Executable | 📄 = Regular file")
