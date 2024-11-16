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

    # Extract lattice points from the thresholded image (non-zero pixel locations)
    lattice_points = np.column_stack(np.where(thresholded > 127))  # Extract the coordinates of white pixels (lattice)

    # Normalize lattice points to fit into the 3D volume
    lattice_points_normalized = lattice_points / np.max(lattice_points, axis=0)  # Normalize to [0, 1] range

    # Generate 3D Shape
    st.subheader("Generated Volumetric Shape")
    if shape_choice == "Cube":
        mesh = trimesh.creation.box(extents=(length, length, length))
    elif shape_choice == "Cylinder":
        mesh = trimesh.creation.cylinder(radius=radius, height=height)
    elif shape_choice == "Sphere":
        mesh = trimesh.creation.icosphere(radius=radius)

    # Convert Trimesh to Plotly Mesh3D
    vertices = np.array(mesh.vertices)
    faces = np.array(mesh.faces)
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    i, j, k = faces[:, 0], faces[:, 1], faces[:, 2]

    # Create lattice as small spheres (or cubes) to overlay on the volumetric shape
    lattice_radius = 0.5  # Adjust size of lattice points (small spheres)

    # Depending on shape, distribute lattice points across the entire volume

    if shape_choice == "Cube":
        # Spread the points over the 3D volume of the cube
        lattice_x = lattice_points_normalized[:, 1] * length  # Scale to the cube dimensions
        lattice_y = lattice_points_normalized[:, 0] * length
        lattice_z = np.random.uniform(0, length, size=lattice_x.shape)  # Randomly place in Z-axis for the cube

    elif shape_choice == "Cylinder":
        # For cylinder, map the lattice points to the cylindrical coordinates
        lattice_x = lattice_points_normalized[:, 1] * radius  # Scale to the cylinder radius
        lattice_y = lattice_points_normalized[:, 0] * radius
        lattice_z = np.random.uniform(0, height, size=lattice_x.shape)  # Randomly place in Z-axis for the cylinder

    elif shape_choice == "Sphere":
        # For sphere, convert the normalized lattice points into spherical coordinates
        theta = np.linspace(0, 2 * np.pi, len(lattice_points_normalized))
        phi = np.arccos(2 * lattice_points_normalized[:, 0] - 1)  # Map points to spherical coords
        lattice_x = radius * np.sin(phi) * np.cos(theta)
        lattice_y = radius * np.sin(phi) * np.sin(theta)
        lattice_z = radius * np.cos(phi)

    # Plot the shape and lattice
    fig = go.Figure()

    # 3D Mesh for Volumetric Shape
    fig.add_trace(go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        opacity=0.5,
        color="cyan",
        name="Volumetric Shape"
    ))

    # Lattice points as small spheres
    fig.add_trace(go.Scatter3d(
        x=lattice_x,
        y=lattice_y,
        z=lattice_z,
        mode='markers',
        marker=dict(size=4, color="red", opacity=0.7),
        name="Lattice Points"
    ))

    fig.update_layout(
        scene=dict(aspectmode="data"),
        margin=dict(l=0, r=0, b=0, t=0),
        title="Volumetric Shape with Lattice"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Provide Download Option for the 3D Model
    st.subheader("Download the 3D Model")
    model_bytes = mesh.export(file_type='stl')
    st.download_button("Download STL File", model_bytes, file_name="volumetric_shape_with_lattice.stl")
