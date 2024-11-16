import streamlit as st
import numpy as np
import trimesh
import plotly.graph_objects as go
import cv2

# Streamlit App Title
st.title("Cellular Lattice to Volumetric Shape Converter")

# Sidebar for User Options
st.sidebar.header("Options")
shape_choice = st.sidebar.selectbox("Select the volumetric shape", ["Cube", "Cylinder", "Sphere"])

# User Inputs for Shape Parameters
if shape_choice == "Cube":
    length = st.sidebar.number_input("Edge Length (mm)", value=10.0, step=1.0, min_value=1.0)
elif shape_choice == "Cylinder":
    radius = st.sidebar.number_input("Radius (mm)", value=5.0, step=1.0, min_value=1.0)
    height = st.sidebar.number_input("Height (mm)", value=10.0, step=1.0, min_value=1.0)
elif shape_choice == "Sphere":
    radius = st.sidebar.number_input("Radius (mm)", value=5.0, step=1.0, min_value=1.0)

# Upload Image
uploaded_file = st.file_uploader("Upload Cellular Lattice Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Load the image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    st.subheader("Uploaded Cellular Lattice Image")
    st.image(image, caption="Cellular Lattice Structure", use_column_width=True)
    
    # Thresholding to extract lattice 
    _, thresholded = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    # Show Preprocessed Image
    st.subheader("Thresholded Image for Lattice Structure")
    st.image(thresholded, caption="Processed Cellular Lattice", use_column_width=True)

    # Generate lattice structure based on volume and connectivity
    lattice_points = np.column_stack(np.where(thresholded > 127))  # Get the points
    lattice_points_normalized = lattice_points / np.max(lattice_points, axis=0)  # Normalize the points to [0, 1]

    # Create continuous lattice structure (mesh grid)
    lattice_nodes = []
    lattice_edges = []
    
    if shape_choice == "Cube":
        # Create a 3D grid for the cube
        for i in range(0, len(lattice_points_normalized), 3):
            x = lattice_points_normalized[i][1] * length
            y = lattice_points_normalized[i][0] * length
            z = np.random.uniform(0, length)  # Randomly distribute along Z-axis
            lattice_nodes.append((x, y, z))
        
        # Connectivity - Add edges between nodes
        for i in range(len(lattice_nodes) - 1):
            if np.random.random() < 0.2:  # Random connectivity, adjust probability as needed
                lattice_edges.append((i, i + 1))  # Connect node i to node i + 1

    elif shape_choice == "Cylinder":
        # Create cylindrical lattice points
        for i in range(0, len(lattice_points_normalized), 3):
            x = lattice_points_normalized[i][1] * radius
            y = lattice_points_normalized[i][0] * radius
            z = np.random.uniform(0, height)
            lattice_nodes.append((x, y, z))
        
        # Connectivity - Add edges between nodes in the cylindrical volume
        for i in range(len(lattice_nodes) - 1):
            if np.random.random() < 0.2:
                lattice_edges.append((i, i + 1))

    elif shape_choice == "Sphere":
        # Generate spherical lattice points
        theta = np.linspace(0, 2 * np.pi, len(lattice_points_normalized))
        phi = np.arccos(2 * lattice_points_normalized[:, 0] - 1)
        
        for i in range(len(lattice_points_normalized)):
            x = radius * np.sin(phi[i]) * np.cos(theta[i])
            y = radius * np.sin(phi[i]) * np.sin(theta[i])
            z = radius * np.cos(phi[i])
            lattice_nodes.append((x, y, z))
        
        # Connectivity - Add edges between nodes in the spherical volume
        for i in range(len(lattice_nodes) - 1):
            if np.random.random() < 0.2:
                lattice_edges.append((i, i + 1))

    # Convert lattice nodes and edges to mesh
    nodes = np.array(lattice_nodes)
    edges = np.array(lattice_edges)

    # Create a plotly 3D scatter plot with lattice nodes and edges
    fig = go.Figure()

    # Plot nodes as small spheres
    fig.add_trace(go.Scatter3d(
        x=nodes[:, 0],
        y=nodes[:, 1],
        z=nodes[:, 2],
        mode='markers',
        marker=dict(size=3, color="red", opacity=0.7),
        name="Lattice Nodes"
    ))

    # Plot edges as lines
    for edge in edges:
        fig.add_trace(go.Scatter3d(
            x=[nodes[edge[0]][0], nodes[edge[1]][0]],
            y=[nodes[edge[0]][1], nodes[edge[1]][1]],
            z=[nodes[edge[0]][2], nodes[edge[1]][2]],
            mode='lines',
            line=dict(color="blue", width=2),
            name="Lattice Edges"
        ))

    fig.update_layout(
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, b=0, t=0),
        title="Volumetric Shape with Lattice Structure"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Provide Download Option for the 3D Model
    st.subheader("Download the 3D Model")
    # Export to a 3D file format
    model_bytes = trimesh.Trimesh(vertices=nodes, faces=edges).export(file_type='stl')
    st.download_button("Download STL File", model_bytes, file_name="volumetric_shape_with_lattice.stl")
