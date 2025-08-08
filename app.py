import streamlit as st
import subprocess
import os

# Set page configuration
st.set_page_config(
    page_title="File Explorer App",
    page_icon="📁",
    layout="wide"
)

# Display the main title
st.title("Hello")
st.subheader("Server File Explorer")

# Function to run shell command safely
def run_shell_command(command):
    try:
        # Run the command and capture output
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=10  # Timeout after 10 seconds
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"

# Display current working directory
st.markdown("### Current Directory:")
current_dir = os.getcwd()
st.code(current_dir)

# Run ls command and display results
st.markdown("### Files and Folders:")

# Get the file listing
file_list = run_shell_command("ls -la")

if file_list.startswith("Error:"):
    st.error(file_list)
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
                    # Add emoji based on file type
                    if permissions.startswith('d'):
                        st.text(f"📁 {name}")
                    elif permissions[3] == 'x':
                        st.text(f"⚡ {name}")
                    else:
                        st.text(f"📄 {name}")

# Add refresh button
if st.button("🔄 Refresh File List"):
    st.rerun()

# Add some spacing
st.markdown("---")
st.caption("This app runs 'ls -la' command on the server to show files and directories.")
